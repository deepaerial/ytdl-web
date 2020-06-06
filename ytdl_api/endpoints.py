import uuid
import re

import urllib
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import AnyHttpUrl
from starlette.responses import RedirectResponse

from . import __version__, __youtube_dl_version__, schemas, task

router = APIRouter()


@router.get("/session/init", response_class=RedirectResponse, status_code=307)
async def session_init(request: Request):
    request.session.update({"u_id": uuid.uuid4().hex})
    return RedirectResponse(request.url_for("session_check"))


@router.get(
    "/session/check",
    status_code=200,
    response_model=schemas.StatusResponse,
    responses={401: {"model": schemas.NoValidSessionError}},
)
async def session_check(request: Request):
    if not request.session.get("u_id"):
        raise HTTPException(401, "No valid session")
    return {}


@router.get("/version", response_model=schemas.VersionResponse, status_code=200)
async def api_version():
    """
    Endpoint for getting info about server API.
    """
    return {
        "youtube_dl_version": __youtube_dl_version__,
        "api_version": __version__,
    }


@router.get("/info/", response_model=schemas.InfoResponse)
async def video_info(video_url: AnyHttpUrl):
    """
    Endpoint for getting info about video
    """
    if not re.match(r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$", video_url):
        return {
            "video_url": video_url,

        }
    parsed_url = urllib.parse.urlparse(video_url)
    video_id = urllib.parse.parse_qs(parsed_url.query)["v"][0]
    return {
        "video_url": video_url,
        "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/0.jpg",
    }


@router.put("/download", response_model=schemas.StatusResponse, status_code=201)
async def download(
    json_params: schemas.DownloadParamsModel, task_queue: BackgroundTasks
):
    """
    Endpoint for fetching video from Youtube and converting it to
    specified format.
    """
    task_queue.add_task(task.download_task, json_params.params)
    return {}
