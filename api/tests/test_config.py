from pathlib import Path
from typing import Iterable

import pytest
from confz import ConfZDataSource
from fastapi.testclient import TestClient

from ytdl_api.config import Settings
from ytdl_api.dependencies import get_settings


@pytest.fixture()
def settings(fake_media_path: Path) -> Iterable[Settings]:
    data_source = ConfZDataSource(
        data={
            "allow_origins": ["*"],
            "downloader": "mocked",
            "datasource": {"deta_key": "*****", "deta_base": "*****"},
            "storage": {"path": fake_media_path},
            "disable_docs": True,
        }
    )
    with Settings.change_config_sources(data_source):
        yield Settings()  # type: ignore


@pytest.fixture
def app(settings: Settings):
    app = settings.init_app()
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


def test_no_docs_if_disabled(app: TestClient):
    """
    Test if Swagger is disabled if disable_docs config is set to True.
    """
    response = app.get("/docs")
    assert response.status_code == 404
