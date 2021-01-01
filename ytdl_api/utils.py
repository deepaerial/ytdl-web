import re
import uuid
import asyncio
import typing
from pathlib import Path
import youtube_dl

from . import schemas
from .config import settings
from .db import DAOInterface


def get_unique_id() -> str:
    return uuid.uuid4().hex


def video_info(
    download_params: schemas.YTDLParams, datasource: DAOInterface
) -> schemas.Download:
    """
    Fetch video info data.
    """
    if not re.match(
        r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$", download_params.url
    ):
        raise Exception("Unsuported we resource url")
    existing_download = datasource.get_download_if_exists(
        download_params.url, download_params.media_format
    )
    if existing_download:
        download = existing_download.copy(exclude={"media_id"}, deep=True)
        download.media_id = get_unique_id()
        return download
    media_id = get_unique_id()
    ytdl_params = download_params.get_youtube_dl_params(media_id)
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
        file_path = Path(settings.media_path / f"{media_id}.{media_format}")
        thumbnail_data = info_dict["thumbnails"][-1]
        download = schemas.Download(
            media_id=media_id,
            media_format=media_format,
            duration=info_dict["duration"] * 1000,  # Duration in milliseconds
            filesize=filesize,  # size in bytes,
            title=title,
            status=schemas.ProgressStatusEnum.STARTED.value,
            video_url=download_params.url,
            thumbnail=schemas.ThumbnailInfo(
                url=thumbnail_data["url"],
                width=thumbnail_data["width"],
                height=thumbnail_data["height"],
            ),
        )
        download._file_path = file_path
    return download


def download(
    download_params: schemas.YTDLParams,
    media_id: str,
    progress_hook: typing.Optional[typing.Callable[[dict], None]],
) -> int:
    """
    Download task

    Options:
    https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/options.py
    """
    ytdl_params = download_params.get_youtube_dl_params(media_id)
    if progress_hook:
        ytdl_params["progress_hooks"] = [
            lambda data: asyncio.run(progress_hook(data))
        ]
    with youtube_dl.YoutubeDL(ytdl_params) as ydl:
        result_status = ydl.download([download_params.url])
    if result_status == 0:
        pass
    return result_status
