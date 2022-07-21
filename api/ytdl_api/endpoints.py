import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, Request, HTTPException
from fastapi.responses import FileResponse
from pydantic.networks import AnyHttpUrl
from sse_starlette.sse import EventSourceResponse
from starlette import status

from . import config, datasource, dependencies
from .converters import create_download_from_download_params
from .downloaders import IDownloader
from .queue import NotificationQueue
from .schemas import requests, responses
from .constants import DonwloadStatus
from .types import OnDownloadCallback
from .callbacks import on_start_converting, on_finish_callback

router = APIRouter(tags=["base"])


@router.get(
    "/version", response_model=responses.VersionResponse, status_code=status.HTTP_200_OK
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
    uid: str, datasource: datasource.IDataSource = Depends(dependencies.get_database),
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
    url: AnyHttpUrl, downloader: IDownloader = Depends(dependencies.get_downloader),
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
    uid: str,
    download_params: requests.DownloadParams,
    background_tasks: BackgroundTasks,
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
    downloader: IDownloader = Depends(dependencies.get_downloader),
    progress_hook: OnDownloadCallback = Depends(dependencies.get_on_progress_hook),
):
    """
    Endpoint for fetching video from Youtube and converting it to
    specified format.
    """
    download = create_download_from_download_params(uid, download_params, downloader)
    datasource.put_download(download)
    background_tasks.add_task(
        downloader.download,
        download,
        progress_hook,
        on_start_converting,
        on_finish_callback,
    )
    return {"downloads": datasource.fetch_downloads(uid)}


# TODO: write unittest for endpoint
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
    uid: str,
    media_id: str,
    datasource: datasource.IDataSource = Depends(dependencies.get_database),
):
    """
    Endpoint for downloading fetched video from Youtube.
    """
    media_file = datasource.get_download(uid, media_id)
    if media_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Download not found"
        )
    if media_file.status != DonwloadStatus.FINISHED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not downloaded yet"
        )
    if media_file.file_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Downloaded file not found"
        )
    media_file.status = DonwloadStatus.DOWNLOADED
    datasource.put_download(media_file)
    return FileResponse(
        media_file.file_path,
        media_type="application/octet-stream",
        filename=media_file.filename,
    )


@router.get("/download/stream", response_class=EventSourceResponse)
async def fetch_stream(
    uid: str,
    request: Request,
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
                yield data.json()

    return EventSourceResponse(_stream())


# @router.delete(
#     "/delete",
#     response_model=schemas.DeleteResponse,
#     status_code=200,
#     responses={
#         404: {
#             "content": {"application/json": {}},
#             "model": schemas.ErrorResponse,
#             "description": "Download not found",
#             "example": {"detail": "Download not found"},
#         },
#         500: {"model": schemas.ErrorResponse},
#     },
# )
# async def delete_media(
#     uid: str,
#     media_id: str,
#     datasource: datasource.IDataSource = Depends(dependencies.get_database),
# ):
#     """
#     Endpoint for deleting downloaded media.
#     """
#     media_file = datasource.get_download(uid, media_id)
#     if not media_file:
#         raise DOWNLOAD_NOT_FOUND
#     if media_file._file_path.exists():
#         media_file._file_path.unlink()
#     media_file.status = schemas.ProgressStatusEnum.DELETED
#     datasource.update_download(uid, media_file)
#     return {"media_id": media_file.media_id, "status": media_file.status}
