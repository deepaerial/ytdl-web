import pkg_resources
from typing import Generator
from pydantic import parse_obj_as
import pytest
from fastapi.testclient import TestClient

from ytdl_api.schemas.models import Download
from ytdl_api.schemas.requests import DownloadParams
from ytdl_api.datasource import IDataSource
from ytdl_api.constants import MediaFormat


@pytest.fixture()
def mock_download_params() -> DownloadParams:
    return DownloadParams(
        url="https://www.youtube.com/watch?v=NcBjx_eyvxc",
        video_stream_id="136",
        audio_stream_id="251",
        media_format=MediaFormat.MP4,
    )


@pytest.fixture()
def mock_persisted_download(
    app_client: TestClient,
    uid: str,
    datasource: IDataSource,
    mock_download_params: DownloadParams,
) -> Generator[Download, None, None]:
    response = app_client.put(
        "/api/download", cookies={"uid": uid}, json=mock_download_params.dict()
    )
    download = next(
        download
        for download in response.json()["downloads"]
        if download["url"] == mock_download_params.url
    )
    download = parse_obj_as(Download, download)
    yield download
    datasource.delete_download(download)



def test_version_endpoint(app_client: TestClient):
    """
    Test endpoint that returns information about API version.
    """
    response = app_client.get("/api/version")
    json_response = response.json()
    assert response.status_code == 200
    assert "apiVersion" in json_response
    expected_api_version = pkg_resources.get_distribution("ytdl_api").version
    assert json_response["apiVersion"] == expected_api_version


def test_get_downloads(
    uid: str, app_client: TestClient, mock_persisted_download: Download
):
    response = app_client.get("/api/downloads", cookies={"uid": uid})
    assert response.status_code == 200
    json_response = response.json()
    assert "downloads" in json_response
    assert len(json_response) == 1
    assert json_response["downloads"][0]["title"] == mock_persisted_download.title
    assert json_response["downloads"][0]["url"] == mock_persisted_download.url
    assert json_response["downloads"][0]["mediaId"] == mock_persisted_download.media_id


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=NcBjx_eyvxc",
        "https://www.youtube.com/watch?v=TNhaISOUy6Q",
    ],
)
def test_get_preview(app_client: TestClient, url: str):
    response = app_client.get("/api/preview", params={"url": url})
    assert response.status_code == 200
    json_response = response.json()
    assert all(
        field in json_response
        for field in [
            "url",
            "title",
            "thumbnailUrl",
            "duration",
            "mediaFormats",
            "audioStreams",
            "videoStreams",
        ]
    )


def test_submit_download(
    app_client: TestClient, uid: str, mock_download_params: DownloadParams
):
    response = app_client.put(
        "/api/download", cookies={"uid": uid}, json=mock_download_params.dict()
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
            "media_id": mocked_downloaded_media.media_id,
        },
        cookies={"uid": mocked_downloaded_media.client_id},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"


def test_download_file_but_non_exisiting_media_id(
    app_client: TestClient, mocked_downloaded_media: Download
):
    response = app_client.get(
        "/api/download",
        params={
            "media_id": "*****",
        },
        cookies={"uid": mocked_downloaded_media.client_id},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Download not found"


def test_download_file_but_non_existing_client_id(
    app_client: TestClient, mocked_downloaded_media: Download
):
    response = app_client.get(
        "/api/download",
        params={"media_id": mocked_downloaded_media.media_id},
        cookies={"uid": "******"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Download not found"


def test_download_file_but_download_not_finished(
    app_client: TestClient, mock_persisted_download: Download
):
    response = app_client.get(
        "/api/download",
        params={
            "media_id": mock_persisted_download.media_id,
        },
        cookies={"uid": mock_persisted_download.client_id},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "File not downloaded yet"


def test_download_file_but_no_file_present(
    app_client: TestClient, mock_persisted_download_with_finished_status: Download
):
    response = app_client.get(
        "/api/download",
        params={"media_id": mock_persisted_download_with_finished_status.media_id},
        cookies={"uid": mock_persisted_download_with_finished_status.client_id},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Downloaded file is not found"


def test_delete_non_existing_download(app_client: TestClient):
    response = app_client.delete(
        "/api/delete", params={"media_id": -1}, cookies={"uid": "-1"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Download not found"


def test_delete_existing_unfinished_download(
    app_client: TestClient, mock_persisted_download: Download
):
    response = app_client.delete(
        "/api/delete",
        params={
            "media_id": mock_persisted_download.media_id,
        },
        cookies={"uid": mock_persisted_download.client_id},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Media file is not downloaded yet"


def test_delete_existing_download_with_finished_status_but_no_file(
    app_client: TestClient, mock_persisted_download_with_finished_status: Download
):
    response = app_client.delete(
        "/api/delete",
        params={"media_id": mock_persisted_download_with_finished_status.media_id},
        cookies={"uid": mock_persisted_download_with_finished_status.client_id},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Downloaded file is not found"


def test_delete_existing_downloaded_file(
    app_client: TestClient, mocked_downloaded_media: Download
):
    response = app_client.delete(
        "/api/delete",
        params={"media_id": mocked_downloaded_media.media_id},
        cookies={"uid": mocked_downloaded_media.client_id},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert "mediaId" in json_response
    assert json_response["mediaId"] == mocked_downloaded_media.media_id
    assert "status" in json_response
    assert json_response["status"] == "deleted"
