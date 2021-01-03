from fastapi import Depends
from functools import lru_cache
from . import queue, db
from .config import Settings, DbTypes, settings


def get_settings() -> Settings:
    return settings


@lru_cache
def get_notification_queue() -> queue.NotificationQueue:
    return queue.NotificationQueue()


def get_database(settings: Settings = Depends(get_settings)) -> db.DAOInterface:
    db_type = settings.db_type
    if db_type == DbTypes.MEMORY:
        return db.InMemoryDB()
    elif db_type == DbTypes.DETA:
        deta_project_key = settings.deta_key
        deta_base_name = settings.deta_base
        return db.DetaDB(deta_project_key, deta_base_name)
