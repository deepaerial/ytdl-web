import re
import asyncio
import typing
import functools
import youtube_dl

import pytube

from . import schemas
from .logger import YDLLogger
from .config import settings


def video_info(
    download_params: schemas.YTDLParams,
) -> typing.List[schemas.FetchedItem]:
    """
    Fetch video info data.
    """
    downloads = []
    for url in download_params.urls:
        if not re.match(r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$", url):
            downloads.append(schemas.FetchedItem(video_url=url, thumbnail_url=None))
        else:
            ytdl_params = {
                "verbose": True,
                "rm_cachedir": True,
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "outtmpl": (settings.media_path / "%(title)s.%(ext)s")
                .absolute()
                .as_posix(),
                "logger": YDLLogger(),
                "updatetime": download_params.use_last_modified,
                "noplaylist": False,
            }
            with youtube_dl.YoutubeDL(ytdl_params) as ydl:
                info_dict = ydl.extract_info(url, download=False)
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
                thumbnail_data = info_dict["thumbnails"][-1]
            downloads.append(
                schemas.FetchedItem(
                    duration=info_dict["duration"] * 1000,  # Duration in milliseconds
                    filesize=filesize,  # size in bytes,
                    title=title,
                    video_url=url,
                    thumbnail=schemas.ThumbnailInfo(
                        url=thumbnail_data["url"],
                        width=thumbnail_data["width"],
                        height=thumbnail_data["height"],
                    ),
                )
            )
    return downloads


async def download(
    download_params: schemas.YTDLParams,
    progress_hook: typing.Optional[typing.Callable[[dict], None]],
) -> int:
    """
    Download task

    Options:
    https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/options.py
    """
    ytdl_params = {
        "verbose": True,
        "rm_cachedir": True,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "outtmpl": (settings.media_path / download_params.outtmpl)
        .absolute()
        .as_posix(),
        "logger": YDLLogger(),
        "updatetime": download_params.use_last_modified,
        "noplaylist": False,  # download only video if URL refers to playlist and video
    }
    postprocessors = []
    if download_params.media_format.is_audio:
        postprocessors.append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": download_params.media_format.value,
                "preferredquality": "192",
            }
        )
    else:
        postprocessors.append(
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": download_params.media_format.value,
            }
        )
    ytdl_params["postprocessors"] = postprocessors
    if progress_hook:
        if asyncio.iscoroutinefunction(progress_hook):
            def progress_hook_wrapper(data):
                asyncio.create_task(progress_hook(data))
            ytdl_params["progress_hooks"] = [progress_hook_wrapper]
        else:
            ytdl_params["progress_hooks"] = [progress_hook]

    with youtube_dl.YoutubeDL(ytdl_params) as ydl:
        result_status = ydl.download(download_params.urls)
    if result_status == 0:
        pass
    return result_status


async def download_pytube(
    download_params: schemas.YTDLParams,
    progress_hook: typing.Optional[typing.Callable[[dict], None]],
) -> int:
    '''
    Downloading video using pytube library.
    '''
    pytube.YouTube(
        download_params.urls[0], on_progress_callback=progress_hook
    ).streams.filter(progressive=True).order_by('resolution').first().download()
