import asyncio
import typing
import re
from http.client import RemoteDisconnected
from fastapi import APIRouter, BackgroundTasks, Request, Depends, HTTPException
from starlette.responses import FileResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse
from youtube_dl.utils import DownloadError

from . import dependencies, schemas, config, queue, db
from .downloaders import DownloaderInterface, get_unique_id

router = APIRouter()


_ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")


async def on_youtube_dl_download_error(request, exc: DownloadError):
    return JSONResponse({"detail": _ansi_escape.sub("", str(exc))}, status_code=500)


async def on_remote_disconnected(request, exc: RemoteDisconnected):
    return JSONResponse(
        {"detail": "Remote server encountered problem, please try again..."},
        status_code=500,
    )


@router.get("/info", response_model=schemas.VersionResponse, status_code=200)
async def info(
    uid: typing.Optional[str] = None,
    settings: config.Settings = Depends(dependencies.get_settings),
    datasource: db.DAOInterface = Depends(dependencies.get_database),
):
    """
    Endpoint for getting info about server API.
    """
    if uid is None:
        uid = get_unique_id()
    return {
        "youtube_dl_version": settings.youtube_dl_version,
        "api_version": settings.version,
        "media_options": [
            media_format.value for media_format in schemas.MediaFormatOptions
        ],
        "uid": uid,
        "downloads": datasource.fetch_downloads(uid),
    }


@router.put("/fetch", response_model=schemas.FetchedListResponse, status_code=201)
async def fetch_media(
    uid: str,
    json_params: schemas.YTDLParams,
    datasource: db.DAOInterface = Depends(dependencies.get_database),
    downloader: DownloaderInterface = Depends(dependencies.get_downloader),
):
    """
    Endpoint for fetching video from Youtube and converting it to
    specified format.
    """
    download = downloader.get_video_info(json_params)
    datasource.put_download(uid, download)
    downloader.submit_download_task(
        uid, download.media_id, json_params,
    )
    return {"downloads": datasource.fetch_downloads(uid)}


@router.get("/fetch")
def download_media(
    uid: str,
    media_id: str,
    datasource: db.DAOInterface = Depends(dependencies.get_database),
):
    """
    Endpoint for downloading fetched video from Youtube.
    """
    media_file = datasource.get_download(uid, media_id)
    if not media_file:
        raise HTTPException(status_code=404, detail="Download not found")
    return media_file.prepare_file_response()


@router.get("/fetch/stream")
async def fetch_stream(
    uid: str,
    request: Request,
    event_queue: queue.NotificationQueue = Depends(dependencies.get_notification_queue),
    datasource: db.DAOInterface = Depends(dependencies.get_database),
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
