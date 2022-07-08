import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient
from fastapi import BackgroundTasks

from ytdl_api.dependencies import get_settings
from ytdl_api.datasource import IDataSource, InMemoryDB
from ytdl_api.config import Settings, DbTypes, DownloadersTypes
from ytdl_api.queue import NotificationQueue
from ytdl_api.downloaders import YoutubeDLDownloader, PytubeDownloader, get_unique_id


@pytest.fixture()
def uid() -> str:
    return get_unique_id()


@pytest.fixture
def temp_directory():
    tmp = TemporaryDirectory()
    yield tmp
    tmp.cleanup()


@pytest.fixture
def fake_media_path(temp_directory: TemporaryDirectory):
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
def youtube_dl_downloader(fake_media_path, fake_db, task_queue):
    return YoutubeDLDownloader(
        media_path=fake_media_path,
        datasource=fake_db,
        event_queue=NotificationQueue(DownloadersTypes.YOUTUBE_DL),
        task_queue=task_queue,
    )


@pytest.fixture
def pytube_downloader(fake_media_path, fake_db, task_queue):
    return PytubeDownloader(
        media_path=fake_media_path,
        datasource=fake_db,
        event_queue=NotificationQueue(DownloadersTypes.PYTUBE),
        task_queue=task_queue,
    )


@pytest.fixture()
def mock_datasource() -> IDataSource:
    return InMemoryDB()


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
