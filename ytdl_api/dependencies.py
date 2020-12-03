from functools import lru_cache
from . import queue, db
from .config import Settings, settings


def get_settings() -> Settings:
    return settings


@lru_cache
def get_notification_queue() -> queue.NotificationQueue:
    return queue.NotificationQueue()


@lru_cache
def get_database() -> db.DAOInterface:
    return db.InMemoryDB()
