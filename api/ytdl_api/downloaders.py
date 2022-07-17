import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

import ffmpeg
from pydantic.networks import AnyHttpUrl
from pytube import YouTube, StreamQuery
from ytdl_api.types import OnDownloadProgressCallback

from .datasource import IDataSource
from .queue import NotificationQueue
from .schemas.models import AudioStream, Download, VideoStream
from .schemas.responses import VideoInfoResponse


class DownloaderInterface(ABC):
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
    def get_video_info(self, url: AnyHttpUrl) -> VideoInfoResponse:  # pragma: no cover
        """
        Abstract method for retrieving information about media resource.
        """
        raise NotImplementedError()

    @abstractmethod
    def download(
        self,
        download: Download,
        progress_hook: Optional[OnDownloadProgressCallback] = None,
    ):  # pragma: no cover
        """
        Abstract method for downloading media given download parameters.
        """
        raise NotImplementedError()


class MockDownloader(DownloaderInterface):
    """
    Mock downloader made primarly for endpoint testing purposes.
    """

    def get_video_info(self, url: AnyHttpUrl) -> VideoInfoResponse:
        video_info = VideoInfoResponse(
            url="https://www.youtube.com/watch?v=B8WgNGN0IVA",
            title="Adam Knight - I've Got The Gold (Shoby Remix)",
            thumbnail_url="https://img.youtube.com/vi/B8WgNGN0IVA/0.jpg",
            video_streams=[
                VideoStream(id="134", resolution="720p", mimetype="video/mp4"),
            ],
            audio_streams=[
                AudioStream(id="134", bitrate="128kbps", mimetype="audio/webm"),
            ],
            duration=100000,
        )
        return video_info

    def download(
        self,
        download: Download,
        progress_hook: Optional[OnDownloadProgressCallback] = None,
    ):
        """
        Simulating download process
        """
        file_path = self.media_path / f"{download.media_id}.{download.media_format}"
        file_path.touch()
        return 0


class PytubeDownloader(DownloaderInterface):
    """
    Downloader based on pytube library
    """

    def get_video_info(self, url: Union[AnyHttpUrl, str]) -> VideoInfoResponse:
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
            for stream in streams.filter(only_video=True, subtype="webm")
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
        self, stream_id: str, media_id: str, streams: StreamQuery
    ) -> Path:
        stream = streams.get_by_itag(stream_id)
        downloaded_stream_file_path = stream.download(
            self.media_path.as_posix(), filename_prefix=f"{stream_id}_{media_id}"
        )
        return Path(downloaded_stream_file_path)

    def download(
        self,
        download: Download,
        progress_hook: Optional[OnDownloadProgressCallback] = None,
    ):
        kwargs = {}
        if progress_hook is not None:
            kwargs[
                "on_progress_callback"
            ] = lambda stream, chunk, bytes_remaining: asyncio.run(
                progress_hook(stream, chunk, bytes_remaining)
            )
        streams = YouTube(download.url, **kwargs).streams.filter(is_dash=True).desc()
        downloaded_streams_file_paths = []
        # Downloading video stream if chosen
        if download.video_stream_id:
            video_file_path = self.__download_stream(
                download.video_stream_id, download.media_id, streams
            )
            downloaded_streams_file_paths.append(video_file_path)
        # Downloading audio stream if chosen
        if download.audio_stream_id is not None:
            audio_file_path = self.__download_stream(
                download.audio_stream_id, download.media_id, streams
            )
            downloaded_streams_file_paths.append(audio_file_path)
        # Converting to chosen format
        downloaded_streams = [
            ffmpeg.input(stream_file_path)
            for stream_file_path in downloaded_streams_file_paths
        ]
        converted_file_path = (
            self.media_path / f"{download.media_id}.{download.media_format}"
        )
        out, err = (
            ffmpeg.concat(*downloaded_streams)
            .output(converted_file_path.as_posix())
            .run(capture_stdout=True, capture_stderr=True)
        )
        download.file_path = converted_file_path
        # Cleaning downloaded streams
        for stream_path in downloaded_streams_file_paths:
            Path(stream_path).unlink()
