
from fastapi import APIRouter, BackgroundTasks

from . import __version__, __youtube_dl_version__
from . import schemas
from . import task


router = APIRouter()


@router.get("/version", response_model=schemas.InfoResponse)
async def api_version():
    """
    Endpoint for getting info about server API.
    """
    return {
        "youtube_dl_version": __youtube_dl_version__,
        "api_version": __version__,
    }


@router.post("/download", response_model=schemas.DownloadResponse)
async def download(
    json_params: schemas.DownloadParamsModel, task_queue: BackgroundTasks
):
    """
    Endpoint for fetching video from Youtube and converting it to
    specified format.
    """
    task_queue.add_task(task.download_task, json_params.params, json_params.socketio_sid)
    return {}
