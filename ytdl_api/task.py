import re
import urllib
import typing
import youtube_dl

from pydantic import UUID4

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
                "format": download_params.video_format,
                "outtmpl": (settings.media_path / "%(title)s.%(ext)s")
                .absolute()
                .as_posix(),
                "logger": YDLLogger(),
                "updatetime": download_params.use_last_modified,
                "noplaylist": False,
            }
            postprocessors = []

            if download_params.audio_format:
                postprocessors.append(
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": download_params.audio_format.value,
                        "preferredquality": "192",
                    }
                )
                choosen_format = download_params.audio_format.value
            elif download_params.video_format:
                postprocessors.append(
                    {
                        "key": "FFmpegVideoConvertor",
                        "preferedformat": download_params.video_format.value,
                    }
                )
                choosen_format = download_params.video_format.value
            ytdl_params["postprocessors"] = postprocessors
            with youtube_dl.YoutubeDL(ytdl_params) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                if download_params.video_format:
                    filesize = [
                        _format["filesize"]
                        for _format in info_dict["formats"]
                        if _format["ext"] == choosen_format or _format["ext"] 
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


def download(
    download_params: schemas.YTDLParams,
    download_id: UUID4,
    socketio_client: str = None,
    outtmpl: str = "%(title)s.%(ext)s",
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
        "outtmpl": (settings.media_path / outtmpl).absolute().as_posix(),
        "logger": YDLLogger(),
        "updatetime": download_params.use_last_modified,
        "noplaylist": False,  # download only video if URL refers to playlist and video
    }

    postprocessors = []

    if download_params.audio_format:
        postprocessors.append(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": download_params.audio_format.value,
                "preferredquality": "192",
            }
        )
    elif download_params.video_format:
        postprocessors.append(
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": download_params.video_format.value,
            }
        )

    ytdl_params["postprocessors"] = postprocessors

    if socketio_client:

        def _get_hook_for_download(download_id):
            def progress_hook(data: dict):
                if data["status"] == "finished":
                    pass

            return progress_hook

        ytdl_params["progress_hooks"] = [_get_hook_for_download(download_id)]

    with youtube_dl.YoutubeDL(ytdl_params) as ydl:
        result_status = ydl.download(download_params.urls)
    if result_status == 0:
        pass
    return result_status
