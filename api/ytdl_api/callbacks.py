from ytdl_api.constants import ProgressStatusEnum
from .queue import NotificationQueue
from .schemas.models import DownloadProgress


async def on_pytube_progress_callback(
    queue: NotificationQueue, client_id, media_id, stream, chunk, bytes_remaining
):
    # TODO: fix creating download progress from pytube callback data
    download_proress = DownloadProgress(
        client_id=client_id,
        media_id=media_id,
        status=ProgressStatusEnum.DOWNLOADING,
        progress=0,
    )
    return await queue.put(client_id, download_proress)
