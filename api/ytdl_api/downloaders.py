import asyncio
from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from typing import Dict, Literal, Optional, Callable, Coroutine, Any

import ffmpeg
from pytube import StreamQuery, YouTube

from .constants import DownloadStatus
from .datasource import IDataSource
from .queue import NotificationQueue
from .schemas.models import AudioStream, Download, VideoStream
from .schemas.responses import VideoInfoResponse
from .types import VideoURL


class IDownloader(ABC):
    """
    Base interface for media downloader class.
    """

    def __init__(
        self, media_path: Path, datasource: IDataSource, event_queue: NotificationQueue
    ):
        self.media_path = media_path
        self.datasource = datasource
        self.event_queue = event_queue

    @abstractmethod
    def get_video_info(self, url: VideoURL) -> VideoInfoResponse:  # pragma: no cover
        """
        Abstract method for retrieving information about media resource.
        """
        raise NotImplementedError()

    @abstractmethod
    def download(self, download: Download):  # pragma: no cover
        """
        Abstract method for downloading media given download parameters.
        """
        raise NotImplementedError()


# typing for callback
OnDownloadCallback = Callable[
    [IDataSource, NotificationQueue, Download], Coroutine[Any, Any, Any]
]


class PytubeDownloader(IDownloader):
    """
    Downloader based on pytube library
    """

    def __init__(
        self,
        media_path: Path,
        datasource: IDataSource,
        event_queue: NotificationQueue,
        on_progress_callback: Optional[OnDownloadCallback] = None,
        on_converting_callback: Optional[OnDownloadCallback] = None,
        on_finish_callback: Optional[OnDownloadCallback] = None,
    ):
        super().__init__(media_path, datasource, event_queue)
        self.on_progress_callback = on_progress_callback
        self.on_converting_callback = on_converting_callback
        self.on_finish_callback = on_finish_callback

    def get_video_info(self, url: VideoURL) -> VideoInfoResponse:
        video = YouTube(url)
        streams = video.streams.filter(is_dash=True).desc()
        audio_streams = [
            AudioStream(
                id=str(stream.itag), bitrate=stream.abr, mimetype=stream.mime_type
            )
            for stream in streams.filter(only_audio=True)
        ]
        video_streams = [
            VideoStream(
                id=str(stream.itag),
                resolution=stream.resolution,
                mimetype=stream.mime_type,
            )
            for stream in streams.filter(only_video=True)
        ]
        video_info = VideoInfoResponse(
            url=url,
            title=video.title,
            thumbnail_url=video.thumbnail_url,
            audio_streams=audio_streams,
            video_streams=video_streams,
            duration=video.length,
        )
        return video_info

    def __download_stream(
        self,
        stream_id: Optional[str],
        media_id: str,
        streams: StreamQuery,
        downloaded_streams_aggregation: dict,
        stream_type: Literal["audio", "video"],
    ):
        if stream_id is None:
            return
        stream = streams.get_by_itag(stream_id)
        downloaded_stream_file_path = stream.download(
            self.media_path.as_posix(), filename_prefix=f"{stream_id}_{media_id}"
        )
        downloaded_streams_aggregation[stream_type] = Path(downloaded_stream_file_path)

    def download(
        self,
        download: Download,
    ):
        kwargs = {}
        if self.on_progress_callback is not None:
            on_progress_callback = asyncio.coroutine(
                partial(
                    self.on_progress_callback,
                    self.datasource,
                    self.event_queue,
                    download,
                )
            )
            kwargs[
                "on_progress_callback"
            ] = lambda stream, chunk, bytes_remaining: asyncio.run(
                on_progress_callback(stream, chunk, bytes_remaining)
            )
        modified_timestamp = self.datasource.update_status(
            download.media_id, DownloadStatus.DOWNLOADING
        )
        download.when_started_download = modified_timestamp
        streams = YouTube(download.url, **kwargs).streams.filter(is_dash=True).desc()
        downloaded_streams_file_paths: Dict[str, Path] = {}
        # Downloading audio stream if chosen
        self.__download_stream(
            download.audio_stream_id,
            download.media_id,
            streams,
            downloaded_streams_file_paths,
            "audio",
        )
        # Downloading video stream if chosen
        self.__download_stream(
            download.video_stream_id,
            download.media_id,
            streams,
            downloaded_streams_file_paths,
            "video",
        )
        # Converting to chosen format
        converted_file_path = (
            self.media_path / f"{download.media_id}.{download.media_format}"
        )
        if self.on_converting_callback is not None:
            asyncio.run(
                self.on_converting_callback(self.datasource, self.event_queue, download)
            )
        out, err = (
            ffmpeg.concat(
                ffmpeg.input(downloaded_streams_file_paths["video"].as_posix()),
                ffmpeg.input(downloaded_streams_file_paths["audio"].as_posix()),
                a=1,
                v=1,
            )
            .output(converted_file_path.as_posix())
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        download.file_path = converted_file_path
        self.datasource.put_download(download)
        if self.on_finish_callback is not None:
            asyncio.run(
                self.on_finish_callback(
                    self.datasource, self.event_queue, download, converted_file_path
                )
            )
        # Cleaning downloaded streams
        for stream_path in downloaded_streams_file_paths.values():
            Path(stream_path).unlink()
