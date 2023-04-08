import asyncio
import tempfile
from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from typing import Dict, Literal, Optional, Callable, Coroutine, Any

import ffmpeg
from pytube import StreamQuery, YouTube

from .constants import DownloadStatus

from .callbacks import (
    noop_callback,
    OnDownloadStateChangedCallback,
    OnDownloadFinishedCallback,
)
from .schemas.models import AudioStream, Download, VideoStream
from .schemas.responses import VideoInfoResponse
from .types import VideoURL


class IDownloader(ABC):
    """
    Base interface for media downloader class.
    """

    def __init__(
        self,
        on_download_started_callback: Optional[OnDownloadStateChangedCallback] = None,
        on_progress_callback: Optional[OnDownloadStateChangedCallback] = None,
        on_converting_callback: Optional[OnDownloadStateChangedCallback] = None,
        on_finish_callback: Optional[OnDownloadFinishedCallback] = None,
    ):
        self.on_download_callback_start = on_download_started_callback or noop_callback
        self.on_progress_callback = on_progress_callback or noop_callback
        self.on_converting_callback = on_converting_callback or noop_callback
        self.on_finish_callback = on_finish_callback or noop_callback

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


class PytubeDownloader(IDownloader):
    """
    Downloader based on pytube library
    """

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
        directory_to_download_to: Path,
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
            directory_to_download_to, filename_prefix=f"{stream_id}_{media_id}"
        )
        downloaded_streams_aggregation[stream_type] = Path(downloaded_stream_file_path)

    def download(
        self,
        download: Download,
    ):
        on_progress_callback = asyncio.coroutine(
            partial(
                self.on_progress_callback,
                download,
            )
        )
        kwargs = {
            "on_progress_callback": lambda stream, chunk, bytes_remaining: asyncio.run(
                on_progress_callback(
                    stream=stream, chunk=chunk, bytes_remaining=bytes_remaining
                )
            )
        }
        asyncio.run(self.on_download_callback_start(download))
        streams = YouTube(download.url, **kwargs).streams.filter(is_dash=True).desc()
        downloaded_streams_file_paths: Dict[str, Path] = {}
        with tempfile.TemporaryDirectory() as tmpdir:
            directory_to_download_to = Path(tmpdir)
            # Downloading audio stream if chosen
            self.__download_stream(
                directory_to_download_to,
                download.audio_stream_id,
                download.media_id,
                streams,
                downloaded_streams_file_paths,
                "audio",
            )
            # Downloading video stream if chosen
            self.__download_stream(
                directory_to_download_to,
                download.video_stream_id,
                download.media_id,
                streams,
                downloaded_streams_file_paths,
                "video",
            )
            # Converting to chosen format
            converted_file_path = directory_to_download_to / download.storage_filename
            asyncio.run(self.on_converting_callback(download))
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
            # Finshing donwload process
            asyncio.run(self.on_finish_callback(download, converted_file_path))
