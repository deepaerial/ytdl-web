import typing
import asyncio
from collections import defaultdict


from .schemas import Download, DownloadProgress, DownloadDataInfo


class NotificationQueue:

    queues: typing.Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    async def get(self, client_id: str) -> DownloadProgress:
        queue = self.queues[client_id]
        return await queue.get()

    def get_put(self, client_id: str, media_id: str) -> typing.Coroutine:
        queue = self.queues[client_id]

        async def inner_put(data: DownloadDataInfo):
            return await queue.put(DownloadProgress.from_data(client_id, media_id, data))

        return inner_put

    async def put(self, client_id: str, download: Download):
        queue = self.queues[client_id]
        return await queue.put(DownloadProgress.from_download(client_id, download))