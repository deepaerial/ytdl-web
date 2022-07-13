import typing
import asyncio
from collections import defaultdict


from .schemas.models import DownloadProgress


class NotificationQueue:

    queues: typing.Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    async def get(self, client_id: str) -> DownloadProgress:
        queue = self.queues[client_id]
        return await queue.get()

    async def put(self, client_id: str, download_progress: DownloadProgress):
        queue = self.queues[client_id]
        return await queue.put(download_progress)

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
