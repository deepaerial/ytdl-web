import asyncio
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import StreamingResponse
from starlette import status

from . import config, datasource, dependencies, storage
from .constants import DownloadStatus
from .converters import create_download_from_download_params
from .downloaders import IDownloader
from .queue import NotificationQueue
from .schemas import requests, responses, models
from .types import VideoURL

router = APIRouter(tags=["base"])

get_uid = dependencies.get_uid_dependency_factory()
get_uid_or_403 = dependencies.get_uid_dependency_factory(raise_error_on_empty=True)


@router.get(
    "/version",
    response_model=responses.VersionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_uid)],
)
async def get_api_version(
    settings: config.Settings = Depends(dependencies.get_settings),
):
    """
    Endpoint for getting info about server API and fetching list of downloaded videos.
    """
    return {
        "api_version": settings.version,
    }


@router.get(
    "/downloads",
    response_model=responses.DownloadsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": responses.ErrorResponse}
    },
)
async def get_downloads(
    uid: str = Depends(get_uid_or_403),
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
):
    """
    Endpoint for fetching list of downloaded videos for current client/user.
    """
    downloads = datasource.fetch_downloads(uid)
    return {"downloads": downloads}


@router.get(
    "/preview",
    response_model=responses.VideoInfoResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": responses.ErrorResponse}
    },
)
async def preview(
    url: VideoURL,
    downloader: IDownloader = Depends(dependencies.get_downloader),
):
    """
    Endpoint for getting info about video.
    """
    download = downloader.get_video_info(url)
    return download


@router.put(
    "/download",
    response_model=responses.DownloadsResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(dependencies.validate_download_params)],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": responses.ErrorResponse}
    },
)
async def submit_download(
    download_params: requests.DownloadParams,
    background_tasks: BackgroundTasks,
    uid: str = Depends(get_uid_or_403),
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
    downloader: IDownloader = Depends(dependencies.get_downloader),
):
    """
    Endpoint for fetching video from Youtube and converting it to
    specified format.
    """
    download = create_download_from_download_params(uid, download_params, downloader)
    datasource.put_download(download)
    background_tasks.add_task(downloader.download, download)
    return {"downloads": datasource.fetch_downloads(uid)}


@router.get(
    "/download",
    responses={
        status.HTTP_200_OK: {
            "content": {"application/octet-stream": {}},
            "description": "Downloaded media file",
        },
        status.HTTP_404_NOT_FOUND: {
            "content": {"application/json": {}},
            "model": responses.ErrorResponse,
            "description": "Download not found",
            "example": {"detail": "Download not found"},
        },
    },
)
async def download_file(
    media_id: str,
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
    download_pair: tuple[models.Download, Path] = Depends(
        dependencies.get_download_file
    ),
):
    """
    Endpoint for downloading fetched video from Youtube.
    """
    download, file_path = download_pair
    datasource.update_status(media_id, DownloadStatus.DOWNLOADED)
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=download.filename,
    )


@router.get("/download/stream", response_class=EventSourceResponse)
async def fetch_stream(
    request: Request,
    uid: str = Depends(get_uid_or_403),
    event_queue: NotificationQueue = Depends(dependencies.get_notification_queue),
):
    """
    SSE endpoint for recieving download status of media items.
    """

    async def _stream():
        while True:
            if await request.is_disconnected():
                break
            try:
                data = await event_queue.get(uid)
            except asyncio.QueueEmpty:
                continue
            else:
                yield data.json(by_alias=True)

    return EventSourceResponse(_stream())


@router.delete(
    "/delete",
    response_model=responses.DeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "content": {"application/json": {}},
            "model": responses.ErrorResponse,
            "description": "Download not found",
            "example": {"detail": "Download not found"},
        },
        status.HTTP_400_BAD_REQUEST: {
            "content": {"application/json": {}},
            "model": responses.ErrorResponse,
            "description": "Media is not downloaded",
            "example": {"detail": "Media is not downloaded"},
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": responses.ErrorResponse},
    },
)
async def delete_download(
    media_id: str,
    uid: str = Depends(get_uid_or_403),
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
    storage: storage.IStorage = Depends(dependencies.get_storage),
):
    """
    Endpoint for deleting downloaded media.
    """
    media_file = datasource.get_download(uid, media_id)
    if media_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Download not found"
        )
    if media_file.status not in (DownloadStatus.FINISHED, DownloadStatus.DOWNLOADED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Media file is not downloaded yet",
        )
    storage.remove_download(media_file.file_path)
    datasource.update_status(media_id, DownloadStatus.DELETED)
    return responses.DeleteResponse(
        media_id=media_file.media_id,
        status=DownloadStatus.DELETED,
        isAudio=media_file.media_format.is_audio,
        title=media_file.title,
    )
