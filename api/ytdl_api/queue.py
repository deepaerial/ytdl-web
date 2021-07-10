import typing
import asyncio
from functools import partial
from collections import defaultdict


from .schemas import Download, DownloadProgress
from .config import DownloadersTypes


class NotificationQueue:

    queues: typing.Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    def __init__(self, downloader_type: DownloadersTypes) -> None:
        self.downloader_type = downloader_type

    async def get(self, client_id: str) -> DownloadProgress:
        queue = self.queues[client_id]
        return await queue.get()

    @staticmethod
    async def on_youtube_dl_progress_callback(queue, client_id, media_id, data):
        return await queue.put(
            DownloadProgress.from_youtube_dl_data(client_id, media_id, data)
        )

    @staticmethod
    async def on_pytube_progress_callback(
        queue, client_id, media_id, stream, chunk, bytes_remaining
    ):
        return await queue.put(
            DownloadProgress.from_pytube_data(
                client_id, media_id, stream, chunk, bytes_remaining
            )
        )

    @staticmethod
    async def __noop_callback(**kwargs):  # pragma: no cover
        """
        Empty callback
        """
        pass

    def get_on_progress_callback(
        self, client_id: str, media_id: str
    ) -> typing.Coroutine:
        queue = self.queues[client_id]
        if self.downloader_type == DownloadersTypes.YOUTUBE_DL:
            return partial(
                NotificationQueue.on_youtube_dl_progress_callback,
                queue,
                client_id,
                media_id,
            )
        elif self.downloader_type == DownloadersTypes.PYTUBE:
            return partial(
                NotificationQueue.on_pytube_progress_callback,
                queue,
                client_id,
                media_id,
            )
        return NotificationQueue.__noop_callback

    async def put(self, client_id: str, download: Download):
        queue = self.queues[client_id]
        return await queue.put(DownloadProgress.from_download(client_id, download))
