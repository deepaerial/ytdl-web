import asyncio
import uuid
from typing import Optional, Callable
from pathlib import Path
from abc import ABC, abstractmethod

import youtube_dl
from fastapi import BackgroundTasks

from .db import DAOInterface
from .queue import NotificationQueue
from .schemas import YTDLParams, Download, ThumbnailInfo, ProgressStatusEnum
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
        task_queue: BackgroundTasks
    ):
        self.media_path = media_path
        self.datasource = datasource
        self.event_queue = event_queue
        self.task_queue = task_queue

    @abstractmethod
    def get_video_info(self, download_params: YTDLParams) -> Download:
        """
        Abstract methid for retrieving information about media resource.
        """
        raise NotImplemented

    @abstractmethod
    def download(
        self,
        download_params: YTDLParams,
        media_id: str,
        progress_hook: Optional[Callable[[dict], None]],
    ):
        """
        Abstract method for downloading media given download parameters.
        """
        raise NotImplemented
    
    def submit_download_task(
        self,
        uid: str,
        media_id: str,
        download_params: YTDLParams,
    ):
        """
        Method for executing media_download in background.
        """
        self.task_queue.add_task(
            self.download,
            download_params,
            media_id,
            self.event_queue.get_put(uid, media_id),
        )


class YoutubeDLDoownloader(DownloaderInterface):
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
            download = existing_download.copy(exclude={"media_id"}, deep=True)
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
                filesize=filesize,  # size in bytes,
                title=title,
                status=ProgressStatusEnum.STARTED.value,
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
        progress_hook: Optional[Callable[[dict], None]],
    ):
        """
        Options for youtube-dl:
        https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/options.py
        """
        ytdl_params = self.__get_youtube_dl_params(download_params, media_id)
        if progress_hook:
            ytdl_params["progress_hooks"] = [
                lambda data: asyncio.run(progress_hook(data))
            ]
        with youtube_dl.YoutubeDL(ytdl_params) as ydl:
            result_status = ydl.download([download_params.url])
        if result_status == 0:
            pass
        return result_status
