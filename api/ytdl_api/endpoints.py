import asyncio
import typing
from starlette import status
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic.networks import AnyHttpUrl
from starlette.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from .exceptions import DOWNLOAD_NOT_FOUND
from . import datasource, dependencies, schemas, config, queue
from .downloaders import DownloaderInterface, get_unique_id

router = APIRouter(tags=["base"])


@router.get(
    "/client_info",
    response_model=schemas.VersionResponse,
    status_code=200,
    responses={500: {"model": schemas.ErrorResponse,}},
)
async def client_info(
    uid: typing.Optional[str] = None,
    settings: config.Settings = Depends(dependencies.get_settings),
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
):
    """
    Endpoint for getting info about server API and fetching list of downloaded videos.
    """
    if uid is None:
        uid = get_unique_id()
    return {
        "api_version": settings.version,
        "media_options": [
            media_format.value for media_format in schemas.MediaFormatOptions
        ],
        "uid": uid,
        "downloads": datasource.fetch_downloads(uid),
    }


@router.get(
    "/downloads",
    response_model=schemas.DownloadsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": schemas.ErrorResponse}
    },
)
async def get_downloads(
    uid: str, datasource: datasource.IDataSource = Depends(dependencies.get_database),
):
    """
    Endpoint for fetching list of downloaded videos for current client/user.
    """
    downloads = datasource.fetch_downloads(uid)
    return {"downloads": downloads}


@router.get(
    "/preview",
    response_model=schemas.Download,
    status_code=200,
    responses={500: {"model": schemas.ErrorResponse,}},
)
async def preview(
    url: AnyHttpUrl,
    downloader: DownloaderInterface = Depends(dependencies.get_downloader),
):
    """
    Endpoint for getting info about video.
    """
    download = downloader.get_video_info(url)
    return download


@router.put(
    "/fetch",
    response_model=schemas.DownloadsResponse,
    status_code=201,
    responses={500: {"model": schemas.ErrorResponse,}},
)
async def fetch_media(
    uid: str,
    json_params: schemas.YTDLParams,
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
    downloader: DownloaderInterface = Depends(dependencies.get_downloader),
):
    """
    Endpoint for fetching video from Youtube and converting it to
    specified format.
    """
    download = downloader.get_video_info(json_params.url)
    download.media_format = json_params.media_format
    datasource.put_download(uid, download)
    downloader.submit_download_task(
        uid, download,
    )
    return {"downloads": datasource.fetch_downloads(uid)}


@router.get(
    "/fetch",
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "Downloaded media file",
        },
        404: {
            "content": {"application/json": {}},
            "model": schemas.ErrorResponse,
            "description": "Download not found",
            "example": {"detail": "Download not found"},
        },
    },
)
async def download_media(
    uid: str,
    media_id: str,
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
    event_queue: queue.NotificationQueue = Depends(dependencies.get_notification_queue),
):
    """
    Endpoint for downloading fetched video from Youtube.
    """
    media_file = datasource.get_download(uid, media_id)
    if not media_file:
        raise DOWNLOAD_NOT_FOUND
    if not media_file._file_path.exists():
        raise HTTPException(status_code=404, detail="Downloaded file not found")
    media_file.status = schemas.ProgressStatusEnum.DOWNLOADED
    datasource.put_download(uid, media_file)
    await event_queue.put(uid, media_file)
    return FileResponse(
        media_file.file_path,
        media_type="application/octet-stream",
        filename=media_file.filename,
    )


@router.get("/fetch/stream",)
async def fetch_stream(
    uid: str,
    request: Request,
    event_queue: queue.NotificationQueue = Depends(dependencies.get_notification_queue),
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
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
                datasource.update_download_progress(data)
                yield data.json()

    return EventSourceResponse(_stream())


@router.delete(
    "/delete",
    response_model=schemas.DeleteResponse,
    status_code=200,
    responses={
        404: {
            "content": {"application/json": {}},
            "model": schemas.ErrorResponse,
            "description": "Download not found",
            "example": {"detail": "Download not found"},
        },
        500: {"model": schemas.ErrorResponse},
    },
)
async def delete_media(
    uid: str,
    media_id: str,
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
):
    """
    Endpoint for deleting downloaded media.
    """
    media_file = datasource.get_download(uid, media_id)
    if not media_file:
        raise DOWNLOAD_NOT_FOUND
    if media_file._file_path.exists():
        media_file._file_path.unlink()
    media_file.status = schemas.ProgressStatusEnum.DELETED
    datasource.update_download(uid, media_file)
    return {"media_id": media_file.media_id, "status": media_file.status}
