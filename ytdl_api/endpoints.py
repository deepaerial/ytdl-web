import uuid
import typing

from fastapi import APIRouter, BackgroundTasks, Cookie, Response

from . import __version__, __youtube_dl_version__, schemas, task

router = APIRouter()


def get_UUID4():
    return uuid.uuid4()


@router.get("/check", response_model=schemas.SessionCheckResponse, status_code=200)
async def session_check(response: Response, u_id: typing.Optional[str] = Cookie(None)):
    """
    Endpoint for checking existing downloads.
    """
    content = {"downloads": []}
    if not u_id:
        u_id = get_UUID4().hex
        response.set_cookie(
            key="ytdl_sid", value=u_id, secure=True, httponly=False, samesite="None"
        )
        return content
    return content


@router.get("/version", response_model=schemas.VersionResponse, status_code=200)
async def api_version():
    """
    Endpoint for getting info about server API.
    """
    return {
        "youtube_dl_version": __youtube_dl_version__,
        "api_version": __version__,
        "media_options": [
            media_format.value for media_format in schemas.MediaFormatOptions
        ],
    }


@router.put("/fetch", response_model=schemas.FetchedListResponse, status_code=201)
async def fetch_media(json_params: schemas.YTDLParams, task_queue: BackgroundTasks):
    """
    Endpoint for fetching video from Youtube and converting it to
    specified format.
    """
    downloads = task.video_info(json_params)
    task_queue.add_task(task.download, json_params, get_UUID4())
    return {"downloads": downloads}
