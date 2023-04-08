import secrets
import asyncio
from functools import lru_cache, partial
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper
from starlette import status


from . import datasource, downloaders, queue, storage
from .callbacks import (
    noop_callback,
    on_pytube_progress_callback,
    on_download_start_callback,
    on_finish_callback,
    on_start_converting,
    OnDownloadStateChangedCallback,
)
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


def get_storage(settings: Settings = Depends(get_settings)) -> storage.IStorage:
    return settings.storage.get_storage()


@lru_cache
def get_downloader(
    datasource: datasource.IDataSource = Depends(get_database),
    event_queue: queue.NotificationQueue = Depends(get_notification_queue),
    storage: storage.IStorage = Depends(get_storage),
) -> downloaders.IDownloader:
    on_download_started_hook = asyncio.coroutine(
        partial(on_download_start_callback, datasource=datasource, queue=event_queue)
    )
    on_progress_hook = asyncio.coroutine(
        partial(on_pytube_progress_callback, datasource=datasource, queue=event_queue)
    )
    on_converting_hook = asyncio.coroutine(
        partial(on_start_converting, datasource=datasource, queue=event_queue)
    )
    on_finish_hook = asyncio.coroutine(
        partial(
            on_finish_callback,
            datasource=datasource,
            queue=event_queue,
            storage=storage,
        )
    )
    return downloaders.PytubeDownloader(
        on_download_started_callback=on_download_started_hook,
        on_progress_callback=on_progress_hook,
        on_converting_callback=on_converting_hook,
        on_finish_callback=on_finish_hook,
    )


def validate_download_params(
    download_params: DownloadParams,
    settings: Settings = Depends(get_settings),
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


def get_uid_dependency_factory(raise_error_on_empty: bool = False):
    """
    Factory function fore returning dependency that fetches client ID.
    """

    def get_uid(
        response: Response,
        uid: Optional[str] = Cookie(None),
        settings: Settings = Depends(get_settings),
    ):
        """
        Dependency for fetchng user ID from cookie or setting it in cookie if absent.
        """
        if uid is None and raise_error_on_empty:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No cookie provided :("
            )
        elif uid is None and not raise_error_on_empty:
            uid = secrets.token_hex(16)
            response.set_cookie(
                key="uid",
                value=uid,
                samesite=settings.cookie_samesite,
                secure=settings.cookie_secure,
                httponly=settings.cookie_httponly,
            )
        return uid

    return get_uid
