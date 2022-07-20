from .constants import ProgressStatusEnum
from .datasource import IDataSource
from .queue import NotificationQueue
from .schemas.models import Download, DownloadProgress


async def noop_callback(*args, **kwargs):  # pragma: no cover
    """
    Empty on downaload progess callback
    """
    pass


async def on_pytube_progress_callback(
    datasource: IDataSource,
    queue: NotificationQueue,
    client_id: str,
    media_id: str,
    *args,
    **kwargs
):
    """
    Callback which will be used in Pytube's progress update callback
    """
    download_proress = DownloadProgress(
        client_id=client_id,
        media_id=media_id,
        status=ProgressStatusEnum.DOWNLOADING,
        progress=-1,
    )
    datasource.update_download_progress(download_proress)
    return await queue.put(client_id, download_proress)


async def on_ffmpeg_start_converting(
    datasource: IDataSource, queue: NotificationQueue, download: Download
):
    """
    Callback called once ffmpeg media format converting process is initiated.
    """
    download.status = ProgressStatusEnum.CONVERTING
    datasource.put_download(download)
    await queue.put(
        download.client_id,
        DownloadProgress(
            client_id=download.client_id,
            media_id=download.media_id,
            status=download.status,
            progress=-1,
        ),
    )


async def on_ffmpeg_complete_callback(
    datasource: IDataSource, queue: NotificationQueue, download: Download
):
    """
    Callback which is executed once ffmpeg finished converting files.
    """
    download.status = ProgressStatusEnum.FINISHED
    datasource.put_download(download)
    await queue.put(
        download.client_id,
        DownloadProgress(
            client_id=download.client_id,
            media_id=download.media_id,
            status=download.status,
            progress=100,
        ),
    )
