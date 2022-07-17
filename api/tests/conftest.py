from confz import ConfZDataSource
import pytest
from pathlib import Path
from typing import Iterable
from tempfile import TemporaryDirectory
from fastapi.testclient import TestClient

from ytdl_api.dependencies import get_database, get_settings
from ytdl_api.datasource import IDataSource, InMemoryDB
from ytdl_api.config import MEDIA_PATH, Settings
from ytdl_api.queue import NotificationQueue
from ytdl_api.schemas.models import Download
from ytdl_api.utils import get_unique_id


@pytest.fixture()
def mock_url() -> str:
    return "https://www.youtube.com/watch?v=TNhaISOUy6Q"


@pytest.fixture()
def uid() -> str:
    return get_unique_id()


@pytest.fixture
def temp_directory():
    tmp = TemporaryDirectory()
    yield MEDIA_PATH
    tmp.cleanup()


@pytest.fixture
def fake_media_path(temp_directory: TemporaryDirectory) -> Path:
    return Path(temp_directory.name)


@pytest.fixture
def fake_db():
    return InMemoryDB()


@pytest.fixture
def event_queue():
    return NotificationQueue()


@pytest.fixture()
def mock_datasource() -> IDataSource:
    return InMemoryDB()


@pytest.fixture
def mock_download(uid: str) -> Download:
    return Download(
        client_id=uid,
        title="Some title",
        url="https://www.youtube.com/watch?v=4B24vYj_vaI",
        thumbnail_url="https://img.youtube.com/vi/4B24vYj_vaI/0.jpg",
        duration=100,
    )


@pytest.fixture()
def mock_persisted_download(
    mock_download: Download, mock_datasource: IDataSource,
):
    mock_datasource.put_download(mock_download)
    yield mock_download


@pytest.fixture()
def settings(fake_media_path: Path) -> Iterable[Settings]:
    data_source = ConfZDataSource(
        data={
            "datasource": {"in_memory": True},
            "downloader": "mocked",
            "allow_origins": ["*"],
            "media_path": fake_media_path,
        }
    )
    with Settings.change_config_sources(data_source):
        yield Settings()  # type: ignore


@pytest.fixture
def app_client(settings: Settings, mock_datasource: IDataSource):
    app = settings.init_app()
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_database] = lambda: mock_datasource
    return TestClient(app)
