import pkg_resources
from fastapi.testclient import TestClient

from ytdl_api.schemas.models import Download
from ytdl_api.schemas.requests import DownloadParams


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


def test_get_downloads(
    uid: str, app_client: TestClient, mock_persisted_download: Download
):
    response = app_client.get("/api/downloads", params={"uid": uid})
    assert response.status_code == 200
    json_response = response.json()
    assert "downloads" in json_response
    assert len(json_response) == 1
    assert json_response["downloads"][0]["title"] == mock_persisted_download.title
    assert json_response["downloads"][0]["url"] == mock_persisted_download.url
    assert json_response["downloads"][0]["media_id"] == mock_persisted_download.media_id


def test_get_preview(app_client: TestClient, mock_url: str):
    response = app_client.get("/api/preview", params={"url": mock_url})
    assert response.status_code == 200
    json_response = response.json()
    assert all(
        field in json_response
        for field in [
            "url",
            "title",
            "thumbnail_url",
            "duration",
            "media_formats",
            "audio_streams",
            "video_streams",
        ]
    )


def test_submit_download(
    app_client: TestClient, uid: str, mock_download_params: DownloadParams
):
    response = app_client.put(
        "/api/download", params={"uid": uid}, json=mock_download_params.dict()
    )
    assert response.status_code == 201
    json_response = response.json()
    assert "downloads" in json_response
    assert any(
        download
        for download in json_response["downloads"]
        if download["url"] == mock_download_params.url
    )


def test_download_file_endpoint(
    app_client: TestClient, mocked_downloaded_media: Download
):
    response = app_client.get(
        "/api/download",
        params={
            "uid": mocked_downloaded_media.client_id,
            "media_id": mocked_downloaded_media.media_id,
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"


def test_download_file_but_non_exisiting_media_id(
    app_client: TestClient, mocked_downloaded_media: Download
):
    response = app_client.get(
        "/api/download",
        params={"uid": mocked_downloaded_media.client_id, "media_id": "*****",},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Download not found"


def test_download_file_but_non_existing_client_id(
    app_client: TestClient, mocked_downloaded_media: Download
):
    response = app_client.get(
        "/api/download",
        params={"uid": "******", "media_id": mocked_downloaded_media.media_id,},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Download not found"


def test_download_file_but_download_not_finished(
    app_client: TestClient, mock_persisted_download: Download
):
    response = app_client.get(
        "/api/download",
        params={
            "uid": mock_persisted_download.client_id,
            "media_id": mock_persisted_download.media_id,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "File not downloaded yet"


def test_download_file_but_no_file_present(
    app_client: TestClient, mock_persisted_download_with_finished_status: Download
):
    response = app_client.get(
        "/api/download",
        params={
            "uid": mock_persisted_download_with_finished_status.client_id,
            "media_id": mock_persisted_download_with_finished_status.media_id,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Downloaded file not found"
