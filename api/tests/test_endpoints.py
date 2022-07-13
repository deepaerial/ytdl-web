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


def test_get_downloads(uid: str, app_client: TestClient, mock_datasource: IDataSource):
    download_1 = Download(
        media_id=get_unique_id(),
        title="Some video 1",
        url="https://www.youtube.com/watch?v=TNhaISOUy6Q",
        video_streams=[],
        audio_streams=[],
        duration=1000,
        thumbnail_url="https://i.ytimg.com/vi_webp/TNhaISOUy6Q/maxresdefault.webp",
    )
    mock_datasource.put_download(uid, download_1)
    response = app_client.get("/api/downloads", params={"uid": uid})
    assert response.status_code == 200
    json_response = response.json()
    assert "downloads" in json_response
    assert len(json_response) == 1
    assert json_response["downloads"][0]["title"] == download_1.title
    assert json_response["downloads"][0]["url"] == download_1.url
    assert json_response["downloads"][0]["media_id"] == download_1.media_id
