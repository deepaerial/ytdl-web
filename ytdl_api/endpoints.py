import uuid
import re

import urllib
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from starlette.responses import RedirectResponse

from . import __version__, __youtube_dl_version__, schemas, task

router = APIRouter()


def get_UUID4():
    return uuid.uuid4()


@router.get("/session/init", response_class=RedirectResponse, status_code=307)
async def session_init(request: Request):
    request.session.update({"u_id": get_UUID4().hex})
    return RedirectResponse(request.url_for("session_check"))


@router.get(
    "/session/check",
    status_code=200,
    response_model=schemas.DownloadListResponse,
    responses={401: {"model": schemas.NoValidSessionError}},
)
async def session_check(request: Request):
    if not request.session.get("u_id"):
        raise HTTPException(401, "No valid session")
    return {"downloads": []}


@router.get("/version", response_model=schemas.VersionResponse, status_code=200)
async def api_version():
    """
    Endpoint for getting info about server API.
    """
    return {
        "youtube_dl_version": __youtube_dl_version__,
        "api_version": __version__,
    }


@router.put("/download", response_model=schemas.DownloadListResponse, status_code=201)
async def download_put(json_params: schemas.YTDLParams, task_queue: BackgroundTasks):
    """
    Endpoint for fetching video from Youtube and converting it to
    specified format.
    """
    downloads = []
    for url in json_params.urls:
        if not re.match(r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$", url):
            downloads.append({"video_url": url, "thumbnail_url": None})
        else:
            parsed_url = urllib.parse.urlparse(url)
            video_id = urllib.parse.parse_qs(parsed_url.query)["v"][0]
            downloads.append(
                {
                    "video_url": url,
                    "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/0.jpg",
                }
            )
    task_queue.add_task(task.download_task, json_params, get_UUID4())
    return {"downloads": downloads}
