import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
from fastapi import BackgroundTasks

from ..dependencies import get_settings
from ..db import InMemoryDB
from ..config import Settings, DbTypes, DownloadersTypes
from ..queue import NotificationQueue
from ..downloaders import YoutubeDLDownloader, PytubeDownloader


@pytest.fixture
def temp_directory():
    tmp = TemporaryDirectory()
    yield tmp
    tmp.cleanup()


@pytest.fixture
def fake_media_path(temp_directory):
    return Path(temp_directory.name)


@pytest.fixture
def fake_db():
    return InMemoryDB()


@pytest.fixture
def event_queue():
    return NotificationQueue()


@pytest.fixture
def task_queue():
    return BackgroundTasks()


@pytest.fixture
def youtube_dl_downloader(
    fake_media_path, fake_db, task_queue
):
    return YoutubeDLDownloader(
        media_path=fake_media_path,
        datasource=fake_db,
        event_queue=NotificationQueue(DownloadersTypes.YOUTUBE_DL),
        task_queue=task_queue,
    )

@pytest.fixture
def pytube_downloader(
    fake_media_path, fake_db, task_queue
):
    return PytubeDownloader(
        media_path=fake_media_path,
        datasource=fake_db,
        event_queue=NotificationQueue(DownloadersTypes.PYTUBE),
        task_queue=task_queue
    )


@pytest.fixture
def app_client(fake_media_path):
    settings = Settings(
        media_path=fake_media_path,
        db_type=DbTypes.MEMORY,
        downloader_type=DownloadersTypes.MOCK,
        allow_origins=[],
        disable_docs=True,
    )
    app = settings.init_app()
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)

