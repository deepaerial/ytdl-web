from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator, Iterable

import pytest
from confz import ConfZDataSource
from fastapi.testclient import TestClient

from ytdl_api.callbacks import on_finish_callback
from ytdl_api.config import Settings
from ytdl_api.constants import DonwloadStatus, MediaFormat
from ytdl_api.converters import create_download_from_download_params
from ytdl_api.datasource import IDataSource, InMemoryDB
from ytdl_api.dependencies import get_settings
from ytdl_api.downloaders import IDownloader, MockDownloader
from ytdl_api.queue import NotificationQueue
from ytdl_api.schemas.models import Download
from ytdl_api.schemas.requests import DownloadParams
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
    yield tmp
    tmp.cleanup()


@pytest.fixture
def fake_media_path(temp_directory: TemporaryDirectory) -> Path:
    return Path(temp_directory.name)


@pytest.fixture
def event_queue():
    return NotificationQueue()


@pytest.fixture()
def mock_datasource() -> IDataSource:
    return InMemoryDB()


@pytest.fixture
def mock_downloader(
    fake_media_path: Path, mock_datasource: IDataSource, event_queue: NotificationQueue
) -> MockDownloader:
    return MockDownloader(fake_media_path, mock_datasource, event_queue)


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
def mock_download_params(mock_url: str) -> DownloadParams:
    return DownloadParams(
        url=mock_url,
        video_stream_id="fake_video_stream_id",
        audio_stream_id="fake_audio_stream_id",
        media_format=MediaFormat.MP4,
    )


@pytest.fixture()
def mock_persisted_download(
    mock_download: Download,
    mock_datasource: IDataSource,
) -> Generator[Download, None, None]:
    mock_datasource.put_download(mock_download)
    yield mock_download


@pytest.fixture()
def mock_persisted_download_with_finished_status(
    mock_persisted_download: Download,
    mock_datasource: IDataSource,
):
    mock_persisted_download.status = DonwloadStatus.FINISHED
    mock_datasource.put_download(mock_persisted_download)
    yield mock_persisted_download


@pytest.fixture()
def mocked_downloaded_media(
    uid: str,
    mock_download_params: DownloadParams,
    mock_datasource: IDataSource,
    mock_downloader: IDownloader,
):
    mock_download = create_download_from_download_params(
        uid, mock_download_params, mock_downloader
    )
    mock_datasource.put_download(mock_download)
    mock_downloader.download(mock_download, on_finish_callback=on_finish_callback)
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
    return TestClient(app)
