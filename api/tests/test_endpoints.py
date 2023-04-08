from datetime import datetime

import pkg_resources
import pytest
from fastapi.testclient import TestClient
from pytest_mock.plugin import MockerFixture

from ytdl_api.datasource import IDataSource
from ytdl_api.schemas.models import Download
from ytdl_api.schemas.requests import DownloadParams


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
    assert (
        datetime.fromisoformat(json_response["downloads"][0]["whenSubmitted"])
        == mock_persisted_download.when_submitted
    )


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
    app_client: TestClient,
    uid: str,
    mock_download_params: DownloadParams,
    mocker: MockerFixture,
    clear_datasource: None,
):
    # Mocking BackgroundTasks because we don't actually want to start process of downloading video
    mocker.patch("ytdl_api.endpoints.BackgroundTasks.add_task")
    response = app_client.put(
        "/api/download", cookies={"uid": uid}, json=mock_download_params.dict()
    )
    assert response.status_code == 201
    json_response = response.json()
    assert "downloads" in json_response
    download = next(
        (
            download
            for download in json_response["downloads"]
            if download["url"] == mock_download_params.url
        ),
        None,
    )
    assert download is not None
    assert download["whenSubmitted"] is not None
    assert (
        download["whenStartedDownload"] is None
    )  # download process will probably not start right away so this field should be null
    assert download["whenDownloadFinished"] is None
    assert download["whenFileDownloaded"] is None
    assert download["whenDeleted"] is None


def test_download_file_endpoint(
    app_client: TestClient, mocked_downloaded_media: Download, datasource: IDataSource
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
    download = datasource.get_download(
        mocked_downloaded_media.client_id, mocked_downloaded_media.media_id
    )
    assert download is not None
    assert download.status == "downloaded"
    assert download.when_file_downloaded is not None


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
    app_client: TestClient, mock_persisted_download: Download, datasource: IDataSource
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
    download = datasource.get_download(
        mock_persisted_download.client_id, mock_persisted_download.media_id
    )
    assert download is not None
    assert download.when_started_download is not None


def test_download_file_but_no_file_present(
    app_client: TestClient, mocked_downloaded_media_no_file: Download
):
    response = app_client.get(
        "/api/download",
        params={"media_id": mocked_downloaded_media_no_file.media_id},
        cookies={"uid": mocked_downloaded_media_no_file.client_id},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Download is finished but file not found"


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


def test_delete_existing_downloaded_file(
    app_client: TestClient, mocked_downloaded_media: Download, datasource: IDataSource
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
    download = datasource.get_download(
        mocked_downloaded_media.client_id, mocked_downloaded_media.media_id
    )
    assert download is not None
    assert download.status == "deleted"
    assert download.when_deleted is not None
