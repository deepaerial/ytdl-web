import youtube_dl

from . import schemas, websockets
from .logger import YDLLogger
from .config import settings


def download_task(
    download_params: schemas.YTDLParams,
    socketio_client: str = None,
    outtmpl: str = "%(title)s.%(ext)s",
):
    """
    Download task

    Options: https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/options.py
    """
    ytdl_params = {
        "verbose": True,
        "rm_cachedir": True,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "outtmpl": (settings.media_path / outtmpl).absolute().as_posix(),
        "logger": YDLLogger(),
        "updatetime": download_params.use_last_modified,
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

        def progress_hook(data: dict):
            if data["status"] == "finished":
                websockets.sio.emit(
                    "download_progress",
                    {"status": data["status"]},
                    room=socketio_client,
                )

        ytdl_params["progress_hooks"] = [progress_hook]

    with youtube_dl.YoutubeDL(ytdl_params) as ydl:
        result_status = ydl.download(download_params.urls)
    if result_status == 0:
        pass
    return result_status
