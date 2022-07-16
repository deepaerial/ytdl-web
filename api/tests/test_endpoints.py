from fastapi.testclient import TestClient
import pkg_resources

from ytdl_api.downloaders import get_unique_id
from ytdl_api.schemas.models import Download
from ytdl_api.datasource import IDataSource


def test_version_endpoint(app_client: TestClient):
    """
    Test endpoint that returns information about API version.
    """
    response = app_client.get("/api/version")
    json_response = response.json()
    assert response.status_code == 200
    assert "api_version" in json_response
    expected_api_version = pkg_resources.get_distribution("ytdl_api").version
    assert json_response["api_version"] == expected_api_version


def test_get_downloads(uid: str, app_client: TestClient, mock_persisted_download: Download):
    response = app_client.get("/api/downloads", params={"uid": uid})
    assert response.status_code == 200
    json_response = response.json()
    assert "downloads" in json_response
    assert len(json_response) == 1
    assert json_response["downloads"][0]["title"] == mock_persisted_download.title
    assert json_response["downloads"][0]["url"] == mock_persisted_download.url
    assert json_response["downloads"][0]["media_id"] == mock_persisted_download.media_id
