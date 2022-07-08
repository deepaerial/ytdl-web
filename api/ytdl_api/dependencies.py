from fastapi import Depends, BackgroundTasks
from functools import lru_cache
from . import datasource, queue, downloaders, queue
from .config import Settings, DbTypes, DownloadersTypes

# Ignoring get_settings dependency in coverage because it will
# overridden in unittests. 
@lru_cache
def get_settings() -> Settings: # pragma: no cover
    return Settings()


@lru_cache
def get_notification_queue(settings: Settings = Depends(get_settings)) -> queue.NotificationQueue:
    return queue.NotificationQueue(settings.downloader_type)



def get_database(settings: Settings = Depends(get_settings)) -> datasource.IDataSource:
    db_type = settings.db_type
    if db_type == DbTypes.MEMORY:
        return datasource.InMemoryDB()
    elif db_type == DbTypes.DETA:
        deta_project_key = settings.deta_key
        deta_base_name = settings.deta_base
        return datasource.DetaDB(deta_project_key, deta_base_name)


@lru_cache
def get_downloader(
    task_queue: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    datasource: datasource.IDataSource = Depends(get_database),
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

