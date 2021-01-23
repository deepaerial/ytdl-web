import typing
import asyncio

from fastapi import APIRouter, BackgroundTasks, Request, Depends, HTTPException
from starlette.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from . import dependencies, schemas, utils, config, queue, db

router = APIRouter()


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
        uid = utils.get_unique_id()
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
    task_queue: BackgroundTasks,
    event_queue: queue.NotificationQueue = Depends(dependencies.get_notification_queue),
    datasource: db.DAOInterface = Depends(dependencies.get_database),
):
    """
    Endpoint for fetching video from Youtube and converting it to
    specified format.
    """
    download = utils.video_info(json_params, datasource)
    datasource.put_download(uid, download)
    task_queue.add_task(
        utils.download,
        json_params,
        download.media_id,
        event_queue.get_put(uid, download.media_id),
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
    title = media_file.title
    file_name = f"{title}.{media_file.media_format}"
    file_path = media_file._file_path.absolute().as_posix()
    return FileResponse(
        file_path, media_type="application/octet-stream", filename=file_name
    )


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
