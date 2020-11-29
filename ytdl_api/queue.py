import typing
import asyncio
from collections import defaultdict

from .types import DownloadDataInfo
from .schemas import DownloadProgress


class NotificationQueue:

    queues: typing.Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    async def get(self, topic: str) -> DownloadProgress:
        queue = self.queues[topic]
        return await queue.get()

    def get_put(self, topic: str) -> typing.Coroutine:
        queue = self.queues[topic]

        async def inner_put(data: DownloadDataInfo):
            return await queue.put(DownloadProgress.from_data(topic, data))

        return inner_put
