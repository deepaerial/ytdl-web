from fastapi import Depends
from functools import lru_cache

from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from pydantic.error_wrappers import ErrorWrapper
from . import datasource, downloaders, queue
from .constants import DownloaderTypes
from .schemas.requests import DownloadParams
from .config import Settings, MEDIA_PATH


# Ignoring get_settings dependency in coverage because it will be
# overridden in unittests.
@lru_cache
def get_settings() -> Settings:  # pragma: no cover
    return Settings()  # type: ignore


@lru_cache
def get_notification_queue(
    settings: Settings = Depends(get_settings),
) -> queue.NotificationQueue:
    return queue.NotificationQueue()


def get_database(settings: Settings = Depends(get_settings)) -> datasource.IDataSource:
    return settings.datasource.get_datasource()


@lru_cache
def get_downloader(
    settings: Settings = Depends(get_settings),
    datasource: datasource.IDataSource = Depends(get_database),
    event_queue: queue.NotificationQueue = Depends(get_notification_queue),
) -> downloaders.IDownloader:
    _type = settings.downloader
    # downloader: downloaders.DownloaderInterface
    if _type == DownloaderTypes.PYTUBE:
        downloader = downloaders.PytubeDownloader(MEDIA_PATH, datasource, event_queue)
    elif _type == DownloaderTypes.MOCK:
        downloader = downloaders.MockDownloader(MEDIA_PATH, datasource, event_queue)
    return downloader


def validate_download_params(
    download_params: DownloadParams, settings: Settings = Depends(get_settings),
):
    try:
        if settings.downloader == DownloaderTypes.PYTUBE:
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
