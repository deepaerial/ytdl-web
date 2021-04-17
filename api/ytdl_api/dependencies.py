from fastapi import Depends, BackgroundTasks
from functools import lru_cache
from . import queue, db, downloaders, queue
from .config import Settings, DbTypes, DownloadersTypes


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_notification_queue() -> queue.NotificationQueue:
    return queue.NotificationQueue()


@lru_cache
def get_database(settings: Settings = Depends(get_settings)) -> db.DAOInterface:
    db_type = settings.db_type
    if db_type == DbTypes.MEMORY:
        return db.InMemoryDB()
    elif db_type == DbTypes.DETA:
        deta_project_key = settings.deta_key
        deta_base_name = settings.deta_base
        return db.DetaDB(deta_project_key, deta_base_name)


@lru_cache
def get_downloader(
    task_queue: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    datasource: db.DAOInterface = Depends(get_database),
    event_queue: queue.NotificationQueue = Depends(get_notification_queue),
):
    downloader_type = settings.downloader_type
    if downloader_type == DownloadersTypes.YOUTUBE_DL:
        return downloaders.YoutubeDLDownloader(
            settings.media_path, datasource, event_queue, task_queue
        )
    elif downloader_type == DownloadersTypes.MOCK:
        return downloaders.MockDownloader(
            settings.media_path, datasource, event_queue, task_queue
        )

