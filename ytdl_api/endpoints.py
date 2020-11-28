import typing
import asyncio
import uuid

from fastapi import APIRouter, BackgroundTasks, Request, Depends
from sse_starlette.sse import EventSourceResponse

from . import deps, schemas, task, config, queue

router = APIRouter()


def get_UUID4():
    return uuid.uuid4()


@router.get("/info", response_model=schemas.VersionResponse, status_code=200)
async def info(
    uid: typing.Optional[str] = None,
    settings: config.Settings = Depends(deps.get_settings),
):
    """
    Endpoint for getting info about server API.
    """
    if uid is None:
        uid = get_UUID4().hex
    return {
        "youtube_dl_version": settings.youtube_dl_version,
        "api_version": settings.version,
        "media_options": [
            media_format.value for media_format in schemas.MediaFormatOptions
        ],
        "uid": uid,
    }


@router.put("/fetch", response_model=schemas.FetchedListResponse, status_code=201)
async def fetch_media(
    uid: str,
    json_params: schemas.YTDLParams,
    task_queue: BackgroundTasks,
    event_queue: queue.NotificationQueue = Depends(deps.get_notification_queue),
):
    """
    Endpoint for fetching video from Youtube and converting it to
    specified format.
    """
    downloads = task.video_info(json_params)
    task_queue.add_task(task.download_pytube, json_params, event_queue.get_put(uid))
    return {"downloads": downloads}


@router.get("/fetch/stream")
async def fetch_stream(
    uid: str,
    request: Request,
    event_queue: queue.NotificationQueue = Depends(deps.get_notification_queue)
):
    '''
    SSE endpoint for recieving download status of media items.
    '''
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
