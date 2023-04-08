import os
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator, Iterable, Optional

import pytest
from fastapi.testclient import TestClient
from pydantic import parse_obj_as

from ytdl_api.config import Settings
from ytdl_api.constants import DownloadStatus, MediaFormat
from ytdl_api.datasource import DetaDB, IDataSource
from ytdl_api.dependencies import get_settings
from ytdl_api.schemas.models import Download
from ytdl_api.schemas.requests import DownloadParams
from ytdl_api.utils import get_unique_id

EXAMPLE_VIDEO_PREVIEW = {
    "url": "https://www.youtube.com/watch?v=NcBjx_eyvxc",
    "title": "Madeira | Cinematic FPV",
    "duration": 224,
    "thumbnailUrl": "https://i.ytimg.com/vi/NcBjx_eyvxc/sddefault.jpg",
    "audioStreams": [
        {"id": "251", "mimetype": "audio/webm", "bitrate": "160kbps"},
        {"id": "250", "mimetype": "audio/webm", "bitrate": "70kbps"},
        {"id": "249", "mimetype": "audio/webm", "bitrate": "50kbps"},
        {"id": "140", "mimetype": "audio/mp4", "bitrate": "128kbps"},
        {"id": "139", "mimetype": "audio/mp4", "bitrate": "48kbps"},
    ],
    "videoStreams": [
        {"id": "394", "mimetype": "video/mp4", "resolution": "144p"},
        {"id": "278", "mimetype": "video/webm", "resolution": "144p"},
        {"id": "160", "mimetype": "video/mp4", "resolution": "144p"},
        {"id": "395", "mimetype": "video/mp4", "resolution": "240p"},
        {"id": "242", "mimetype": "video/webm", "resolution": "240p"},
        {"id": "133", "mimetype": "video/mp4", "resolution": "240p"},
        {"id": "396", "mimetype": "video/mp4", "resolution": "360p"},
        {"id": "243", "mimetype": "video/webm", "resolution": "360p"},
        {"id": "134", "mimetype": "video/mp4", "resolution": "360p"},
        {"id": "397", "mimetype": "video/mp4", "resolution": "480p"},
        {"id": "244", "mimetype": "video/webm", "resolution": "480p"},
        {"id": "135", "mimetype": "video/mp4", "resolution": "480p"},
        {"id": "398", "mimetype": "video/mp4", "resolution": "720p"},
        {"id": "247", "mimetype": "video/webm", "resolution": "720p"},
        {"id": "136", "mimetype": "video/mp4", "resolution": "720p"},
        {"id": "399", "mimetype": "video/mp4", "resolution": "1080p"},
        {"id": "248", "mimetype": "video/webm", "resolution": "1080p"},
        {"id": "137", "mimetype": "video/mp4", "resolution": "1080p"},
        {"id": "400", "mimetype": "video/mp4", "resolution": "1440p"},
        {"id": "271", "mimetype": "video/webm", "resolution": "1440p"},
        {"id": "401", "mimetype": "video/mp4", "resolution": "2160p"},
        {"id": "313", "mimetype": "video/webm", "resolution": "2160p"},
    ],
    "mediaFormats": ["mp4", "mp3", "wav"],
}


def get_example_download_instance(
    client_id: str,
    media_format: MediaFormat = MediaFormat.MP4,
    duration: int = 10000,
    filesize: int = 10000,
    status: DownloadStatus = DownloadStatus.STARTED,
    file_path: Optional[Path] = None,
    progress: int = 0,
    when_started_download: Optional[datetime] = None,
) -> Download:
    download_data = {
        **EXAMPLE_VIDEO_PREVIEW,
        "client_id": client_id,
        "media_format": media_format,
        "duration": duration,
        "filesize": filesize,
        "status": status,
        "file_path": file_path,
        "progress": progress,
        "when_started_download": when_started_download,
    }
    return parse_obj_as(Download, download_data)


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


@pytest.fixture()
def fake_media_file_path(fake_media_path: Path) -> Path:
    filename = get_unique_id()
    fake_media_file_path = fake_media_path / filename
    with fake_media_file_path.open("wb") as f:
        file_size_in_bytes = 1024
        f.write(os.urandom(file_size_in_bytes))
    return fake_media_file_path


@pytest.fixture()
def deta_testbase() -> str:
    return "ytdl_test"


@pytest.fixture()
def settings(
    fake_media_path: Path, monkeypatch: pytest.MonkeyPatch, deta_testbase: str
) -> Iterable[Settings]:
    monkeypatch.setenv("DATASOURCE__DETA_BASE", deta_testbase)
    settings = Settings()  # type: ignore
    yield settings


@pytest.fixture()
def datasource(settings: Settings):
    return DetaDB(
        deta_project_key=settings.datasource.deta_key,
        base_name=settings.datasource.deta_base,
    )


@pytest.fixture
def app_client(settings: Settings):
    app = settings.init_app()
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


@pytest.fixture()
def mock_download_params() -> DownloadParams:
    return DownloadParams(
        url=EXAMPLE_VIDEO_PREVIEW["url"],  # type: ignore
        video_stream_id=EXAMPLE_VIDEO_PREVIEW["videoStreams"][12]["id"],  # type: ignore
        audio_stream_id=EXAMPLE_VIDEO_PREVIEW["audioStreams"][0]["id"],  # type: ignore
        media_format=MediaFormat.MP4,
    )


@pytest.fixture()
def clear_datasource(datasource: IDataSource):
    yield
    datasource.clear_downloads()


@pytest.fixture()
def mock_persisted_download(
    uid: str, datasource: IDataSource, clear_datasource
) -> Generator[Download, None, None]:
    download = get_example_download_instance(
        client_id=uid,
        media_format=MediaFormat.MP4,
        status=DownloadStatus.DOWNLOADING,
        when_started_download=datetime.utcnow() - timedelta(minutes=1),
    )
    datasource.put_download(download)
    yield download


@pytest.fixture()
def mocked_downloaded_media(
    uid: str, datasource: IDataSource, fake_media_file_path: Path, clear_datasource
) -> Generator[Download, None, None]:
    download = get_example_download_instance(
        client_id=uid,
        media_format=MediaFormat.MP4,
        duration=1000,
        filesize=1024,
        status=DownloadStatus.FINISHED,
        file_path=fake_media_file_path.as_posix(),
        progress=100,
    )
    datasource.put_download(download)
    yield download


@pytest.fixture()
def mocked_downloaded_media_no_file(
    uid: str, datasource: IDataSource, fake_media_file_path: Path, clear_datasource
) -> Generator[Download, None, None]:
    download = get_example_download_instance(
        client_id=uid,
        media_format=MediaFormat.MP4,
        duration=1000,
        filesize=1024,
        status=DownloadStatus.FINISHED,
        file_path=None,
        progress=100,
    )
    datasource.put_download(download)
    yield download
