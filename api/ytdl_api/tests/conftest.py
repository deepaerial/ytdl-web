import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
from fastapi import BackgroundTasks

from ..dependencies import get_settings
from ..db import DAOInterface, InMemoryDB
from ..config import Settings, DbTypes, DownloadersTypes
from ..queue import NotificationQueue
from ..downloaders import DownloaderInterface, YoutubeDLDownloader


@pytest.fixture
def temp_directory():
    tmp = TemporaryDirectory()
    yield tmp
    tmp.cleanup()


@pytest.fixture
def fake_media_path(temp_directory) -> Path:
    return Path(temp_directory.name)


@pytest.fixture
def fake_db() -> DAOInterface:
    return InMemoryDB()


@pytest.fixture
def event_queue() -> NotificationQueue:
    return NotificationQueue()


@pytest.fixture
def task_queue() -> BackgroundTasks:
    return BackgroundTasks()


@pytest.fixture
def youtube_dl_downloader(
    fake_media_path, fake_db, event_queue, task_queue
) -> DownloaderInterface:
    return YoutubeDLDownloader(
        media_path=fake_media_path,
        datasource=fake_db,
        event_queue=event_queue,
        task_queue=task_queue,
    )


@pytest.fixture
def app_client(fake_media_path) -> TestClient:
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

