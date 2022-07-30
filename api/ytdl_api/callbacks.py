from .constants import DonwloadStatus
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
    download: Download,
    *args,
    **kwargs
):
    """
    Callback which will be used in Pytube's progress update callback
    """
    download_proress = DownloadProgress(
        client_id=download.client_id,
        media_id=download.media_id,
        status=DonwloadStatus.DOWNLOADING,
        progress=-1,
    )
    datasource.update_download_progress(download_proress)
    return await queue.put(download.client_id, download_proress)


async def on_start_converting(
    datasource: IDataSource,
    queue: NotificationQueue,
    download: Download,
):
    """
    Callback called once ffmpeg media format converting process is initiated.
    """
    download.status = DonwloadStatus.CONVERTING
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


async def on_finish_callback(
    datasource: IDataSource,
    queue: NotificationQueue,
    download: Download,
):
    """
    Callback which is executed once ffmpeg finished converting files.
    """
    download.status = DonwloadStatus.FINISHED
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
