import re
import asyncio
import typing
import youtube_dl

from . import schemas


def video_info(
    download_params: schemas.YTDLParams,
) -> typing.List[schemas.FetchedItem]:
    """
    Fetch video info data.
    """
    downloads = []
    if not re.match(r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$", download_params.url):
        downloads.append(schemas.FetchedItem(video_url=download_params.url, thumbnail_url=None))
    else:
        ytdl_params = download_params.get_youtube_dl_params()
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
            thumbnail_data = info_dict["thumbnails"][-1]
        downloads.append(
            schemas.FetchedItem(
                duration=info_dict["duration"] * 1000,  # Duration in milliseconds
                filesize=filesize,  # size in bytes,
                title=title,
                video_url=download_params.url,
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
    progress_hook: typing.Optional[typing.Callable[[dict], None]],
) -> int:
    """
    Download task

    Options:
    https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/options.py
    """
    ytdl_params = download_params.get_youtube_dl_params()
    if progress_hook:
        if asyncio.iscoroutinefunction(progress_hook):
            ytdl_params["progress_hooks"] = [
                lambda data: asyncio.run(progress_hook(data))
            ]
        else:
            ytdl_params["progress_hooks"] = [progress_hook]
    with youtube_dl.YoutubeDL(ytdl_params) as ydl:
        result_status = ydl.download([download_params.url])
    if result_status == 0:
        pass
    return result_status
