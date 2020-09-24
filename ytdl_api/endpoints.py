import uuid
import re
import typing

import urllib
from fastapi import APIRouter, BackgroundTasks, HTTPException, Cookie, Response
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse

from . import __version__, __youtube_dl_version__, schemas, task

router = APIRouter()


def get_UUID4():
    return uuid.uuid4()


@router.get("/check", status_code=200)
async def session_check(response: Response, u_id: typing.Optional[str] = Cookie(None)):
    content = {"downloads": []}
    if not u_id:
        u_id = get_UUID4().hex
        response.set_cookie(key="sid", value=u_id, secure=True, httponly=False, samesite="None")
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
    }


@router.put("/fetch", response_model=schemas.DownloadListResponse, status_code=201)
async def fetch_media(json_params: schemas.YTDLParams, task_queue: BackgroundTasks):
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
