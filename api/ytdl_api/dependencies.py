from functools import lru_cache

from fastapi import Depends
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper

from ytdl_api.types import OnDownloadCallback

from . import datasource, downloaders, queue
from .callbacks import noop_callback, on_pytube_progress_callback
from .config import Settings
from .constants import DownloaderType
from .schemas.requests import DownloadParams


# Ignoring get_settings dependency in coverage because it will be
# overridden in unittests.
@lru_cache
def get_settings() -> Settings:  # pragma: no cover
    return Settings()  # type: ignore


@lru_cache
def get_notification_queue() -> queue.NotificationQueue:
    return queue.NotificationQueue()


def get_database(settings: Settings = Depends(get_settings)) -> datasource.IDataSource:
    return settings.datasource.get_datasource()


@lru_cache
def get_downloader(
    settings: Settings = Depends(get_settings),
    datasource: datasource.IDataSource = Depends(get_database),
    event_queue: queue.NotificationQueue = Depends(get_notification_queue),
) -> downloaders.IDownloader:
    if settings.downloader == DownloaderType.PYTUBE:
        return downloaders.PytubeDownloader(
            settings.media_path, datasource, event_queue
        )
    return downloaders.MockDownloader(settings.media_path, datasource, event_queue)


def get_on_progress_hook(
    settings: Settings = Depends(get_settings),
) -> OnDownloadCallback:
    if settings.downloader == DownloaderType.PYTUBE:
        return on_pytube_progress_callback
    return noop_callback


def validate_download_params(
    download_params: DownloadParams, settings: Settings = Depends(get_settings),
):
    try:
        if settings.downloader == DownloaderType.PYTUBE:
            if not any(
                (download_params.video_stream_id, download_params.audio_stream_id)
            ):
                raise ValueError(
                    "No chosen video or audio stream is choosen for download"
                )
    except ValueError as e:
        validation_error = ValidationError(
            [ErrorWrapper(e, loc="__root__")], download_params.__class__
        )
        raise RequestValidationError(validation_error.raw_errors)
