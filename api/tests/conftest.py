from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

import pytest
from confz import ConfZEnvSource
from fastapi.testclient import TestClient
from ytdl_api.config import Settings
from ytdl_api.dependencies import get_settings
from ytdl_api.datasource import DetaDB
from ytdl_api.utils import get_unique_id

TEST_ENV_FILE = (Path(__file__).parent / ".." / ".env.test").resolve()


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
def settings(fake_media_path: Path, monkeypatch) -> Iterable[Settings]:
    monkeypatch.setenv("MEDIA_PATH", fake_media_path.as_posix())
    config = ConfZEnvSource(
        allow_all=True,
        deny=["title", "description", "version"],
        file=TEST_ENV_FILE,
        nested_separator="__",
    )
    with Settings.change_config_sources(config):
        yield Settings()  # type: ignore


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
