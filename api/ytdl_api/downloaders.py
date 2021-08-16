import asyncio
import pdb
import uuid
from typing import Any, Coroutine, Optional, Callable
from pathlib import Path
from abc import ABC, abstractmethod
from pydantic.networks import AnyHttpUrl

import youtube_dl
import ffmpeg
from pytube import YouTube
from fastapi import BackgroundTasks

from .db import DAOInterface
from .queue import NotificationQueue
from .schemas import (
    AudioStream,
    VideoStream,
    YTDLParams,
    Download,
    ThumbnailInfo,
    ProgressStatusEnum,
    MediaFormatOptions,
)
from .logger import YDLLogger


def get_unique_id() -> str:
    return uuid.uuid4().hex


class DownloaderInterface(ABC):
    """
    Base interface for media downloader class.
    """

    def __init__(
        self,
        media_path: Path,
        datasource: DAOInterface,
        event_queue: NotificationQueue,
        task_queue: BackgroundTasks,
    ):
        self.media_path = media_path
        self.datasource = datasource
        self.event_queue = event_queue
        self.task_queue = task_queue

    @abstractmethod
    def get_video_info(
        self, url: AnyHttpUrl
    ) -> Download:  # pragma: no cover
        """
        Abstract method for retrieving information about media resource.
        """
        raise NotImplemented

    @abstractmethod
    def download(
        self,
        download_params: YTDLParams,
        media_id: str,
        progress_hook: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None,
    ):  # pragma: no cover
        """
        Abstract method for downloading media given download parameters.
        """
        raise NotImplemented

    def submit_download_task(self, uid: str, download: Download):  # pragma: no cover
        """
        Method for executing media_download in background.
        """
        self.task_queue.add_task(
            self.download,
            download,
            self.event_queue.get_on_progress_callback(uid, download.media_id),
        )


class MockDownloader(DownloaderInterface):
    """
    Mock downloader made primarly for endpoint testing purposes.
    """

    def get_video_info(self, url: AnyHttpUrl) -> Download:
        media_id, media_format = get_unique_id(), MediaFormatOptions.MP3
        data = {
            "media_id": media_id,
            "url": "https://www.youtube.com/watch?v=B8WgNGN0IVA",
            "title": "Adam Knight - I've Got The Gold (Shoby Remix)",
            "video_streams": [
                VideoStream(id="134", resolution="720p", mimetype="video/mp4"),
            ],
            "audio_streams": [
                AudioStream(id="134", bitrate="128kbps", mimetype="audio/webm"),
            ],
            "duration": 479000,
            "filesize": 5696217,
            "thumbnail_url": "https://img.youtube.com/vi/B8WgNGN0IVA/0.jpg",
        }
        download = Download(**data)
        download._file_path = self.media_path / f"{media_id}.{media_format}"
        return download

    def download(
        self,
        download: Download,
        progress_hook: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None
    ):
        """
        Simulating download process
        """
        media_id = download.media_id
        media_format = download.media_format
        file_path = self.media_path / f"{media_id}.{media_format}"
        file_path.touch()
        return 0


class YoutubeDLDownloader(DownloaderInterface):
    """
    Downloader that uses youtube-dl for media extraction
    """

    def __get_youtube_dl_params(self, params: YTDLParams, media_id: str) -> dict:
        ytdl_params = {
            "verbose": True,
            "rm_cachedir": True,
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "outtmpl": (self.media_path / f"{media_id}.%(ext)s").absolute().as_posix(),
            "logger": YDLLogger(),
            "updatetime": params.use_last_modified,
            "noplaylist": False,  # download only video if URL refers to playlist and video
        }
        if params.media_format.is_audio:
            ytdl_params["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": params.media_format.value,
                    "preferredquality": "192",
                }
            ]
        else:
            ytdl_params["postprocessors"] = [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": params.media_format.value,
                }
            ]
        return ytdl_params

    def get_video_info(self, download_params: YTDLParams) -> Download:
        existing_download = self.datasource.get_download_if_exists(
            download_params.url, download_params.media_format
        )
        if existing_download:
            download = existing_download.copy(exclude={"media_id", "status"}, deep=True)
            download.media_id = get_unique_id()
            return download
        media_id = get_unique_id()
        ytdl_params = self.__get_youtube_dl_params(download_params, media_id)
        with youtube_dl.YoutubeDL(ytdl_params) as ydl:
            info_dict = ydl.extract_info(download_params.url, download=False)
            if not download_params.media_format.is_audio:
                filesize = [
                    _format["filesize"]
                    for _format in info_dict["formats"]
                    if _format["ext"] == download_params.media_format.value
                    or _format["ext"]
                ][0]
            else:
                filesize = None
            title = info_dict.get("title", None)
            media_format = download_params.media_format
            file_path = self.media_path / f"{media_id}.{media_format}"
            thumbnail_data = info_dict["thumbnails"][-1]
            download = Download(
                media_id=media_id,
                media_format=media_format,
                duration=info_dict["duration"] * 1000,  # Duration in milliseconds
                title=title,
                status=ProgressStatusEnum.STARTED,
                video_url=download_params.url,
                thumbnail=ThumbnailInfo(
                    url=thumbnail_data["url"],
                    width=thumbnail_data["width"],
                    height=thumbnail_data["height"],
                ),
            )
            download._file_path = file_path
        return download

    def download(
        self,
        download_params: YTDLParams,
        media_id: str,
        progress_hook: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None,
    ):
        """
        Options for youtube-dl:
        https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/options.py
        """
        ytdl_params = self.__get_youtube_dl_params(download_params, media_id)
        ytdl_params["progress_hooks"] = [lambda data: asyncio.run(progress_hook(data))]
        with youtube_dl.YoutubeDL(ytdl_params) as ydl:
            result_status = ydl.download([download_params.url])
        if result_status == 0:
            pass
        return result_status


class PytubeDownloader(DownloaderInterface):
    """
    Downloader based on pytube library
    """

    def get_video_info(self, url: AnyHttpUrl) -> Download:
        video = YouTube(url)
        media_id = get_unique_id()
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
        download = Download(
            media_id=media_id,
            url=url,
            title=video.title,
            video_streams=video_streams,
            audio_streams=audio_streams,
            thumbnail_url=video.thumbnail_url,
            duration=video.length,
        )
        return download

    def download(
        self,
        download: Download,
        progress_hook: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None
    ):
        url = download.url
        media_id = download.media_id
        # Chosen video quality
        video_itag = download.video_stream_id
        # Chosen audio quality
        audio_itag = download.audio_stream_id
        # Chosen media format
        media_format = download.media_format
        if not any((video_itag, audio_itag)):
            raise Exception(f"No stream for {url} download was specified. {download}")
        if not media_format:
            raise Exception("No media_format provided.")
        kwargs = {}
        if progress_hook is not None:
            kwargs['on_progress_callback'] = lambda stream, chunk, bytes_remaining: asyncio.run(
                progress_hook(stream, chunk, bytes_remaining)
            )
        streams = (
            YouTube(
                url,
                **kwargs
            )
            .streams.filter(is_dash=True)
            .desc()
        )
        downloaded_streams_file_paths = []
        output_path = self.media_path.as_posix()
        if video_itag:
            video_stream = streams.get_by_itag(video_itag)
            if not video_stream:
                raise Exception(
                    f"Video stream with itag {video_itag} was not found. {download}"
                )
            video_file_path: str = video_stream.download(
                output_path=output_path, filename_prefix=f"{video_itag}_{media_id}",
            )
            downloaded_streams_file_paths.append(video_file_path)
        if audio_itag:
            audio_stream = streams.get_by_itag(audio_itag)
            if not audio_stream:
                raise Exception(
                    f"Audio stream with itag {audio_itag} was not found. {download}"
                )
            audio_file_path: str = audio_stream.download(
                output_path=output_path, filename_prefix=f"{audio_itag}_{media_id}",
            )
            downloaded_streams_file_paths.append(audio_file_path)
        downloaded_streams = [ffmpeg.input(stream_file_path) for stream_file_path in downloaded_streams_file_paths]
        converted_file_path = self.media_path / f"{media_id}.{download.media_format}"
        _ = ffmpeg.concat(
                *downloaded_streams
        ).output(converted_file_path.as_posix()).run(overwrite_output=True)
        download._file_path = converted_file_path
        # Cleaning downloaded streams
        for stream_path in downloaded_streams_file_paths:
            Path(stream_path).unlink()
