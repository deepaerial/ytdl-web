from functools import lru_cache
from . import queue
from .config import settings


def get_settings():
    return settings


@lru_cache
def get_notification_queue():
    return queue.NotificationQueue()
