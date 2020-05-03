import uuid
from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from starlette.responses import RedirectResponse

from . import __version__, __youtube_dl_version__
from . import schemas
from . import task


router = APIRouter()


@router.get("/session/init")
async def session_init(request: Request):
    request.session.update({"u_id": uuid.uuid4().hex})
    return RedirectResponse(request.url_for("session_check"))


@router.get("/session/check", status_code=200, response_model=schemas.StatusResponse)
async def session_check(request: Request):
    if not request.session.get("u_id"):
        raise HTTPException(401, "No valid session")
    return {}


@router.get("/version", response_model=schemas.InfoResponse, status_code=200)
async def api_version():
    """
    Endpoint for getting info about server API.
    """
    return {
        "youtube_dl_version": __youtube_dl_version__,
        "api_version": __version__,
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
