from ..downloaders import get_unique_id
from ..schemas import ProgressStatusEnum


def test_version_endpoint(app_client):
    """
    Test endpoint that returns information about API version.
    """
    response = app_client.get("/api/info")
    assert response.status_code == 200
    assert "api_version" in response.json()
    assert "youtube_dl_version" in response.json()
    assert "uid" in response.json()
    assert "downloads" in response.json()


def test_download_endpoint_no_format(app_client):
    """
    Test endpoint for starting video download task.

    Verify that error raised when no format is passed in POST body.
    """
    response = app_client.put(
        "/api/fetch",
        params={"uid": get_unique_id()},
        json={"url": "https://www.youtube.com/watch?v=0ruMGbPXxbA"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_download_endpoint_bad_url(app_client):
    """
    Test endpoint for starting video download task.

    Verify that error raised when unsupported url is passed in POST body.
    """
    response = app_client.put(
        "/api/fetch",
        params={"uid": get_unique_id()},
        json={"url": "https://www.notube.com/watch?v=0ruMGbPXxbA"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_download_endpoint_video(app_client):
    """
    Test endpoint for starting video download task.

    Verify that video dowload works
    """
    response = app_client.put(
        "/api/fetch",
        params={"uid": get_unique_id()},
        json={
            "url": "https://www.youtube.com/watch?v=0ruMGbPXxbA",
            "media_format": "mp4",
        },
    )
    assert response.status_code == 201
    assert "downloads" in response.json()


def test_download_endpoint_audio(app_client):
    """
    Test endpoint for starting audio download task.

    Verify that audio dowload works
    """
    response = app_client.put(
        "/api/fetch",
        params={"uid": get_unique_id()},
        json={
            "url": "https://www.youtube.com/watch?v=0ruMGbPXxbA",
            "media_format": "mp3",
        },
    )
    assert response.status_code == 201
    assert "downloads" in response.json()


def test_download_fetched_media(app_client, fake_db):
    """
    Test endpoint for fetching downloaded media.
    """
    uid = get_unique_id()
    response = app_client.put(
        "/api/fetch",
        params={"uid": uid},
        json={
            "url": "https://www.youtube.com/watch?v=0ruMGbPXxbA",
            "media_format": "mp3",
        },
    )
    assert response.status_code == 201
    assert "downloads" in response.json()
    download = next(iter(response.json()["downloads"]))
    media_id = download["media_id"]
    response = app_client.get(
        "/api/fetch", params={"uid": uid, "media_id": download["media_id"]}
    )
    assert response.status_code == 200
    download = fake_db.get_download(uid, media_id)
    assert download is not None
    assert download.status == ProgressStatusEnum.DOWNLOADED


def test_download_fetched_media_not_found(app_client):
    response = app_client.get(
        "/api/fetch", params={"uid": "1111", "media_id": "somerandommediaid"}
    )
    assert response.status_code == 404


def test_removed_downloaded_fetched_media(app_client):
    uid = get_unique_id()
    response = app_client.put(
        "/api/fetch",
        params={"uid": uid},
        json={
            "url": "https://www.youtube.com/watch?v=0ruMGbPXxbA",
            "media_format": "mp3",
        },
    )
    assert response.status_code == 201
    assert "downloads" in response.json()
    download = next(iter(response.json()["downloads"]))
    media_id = download["media_id"]
    response = app_client.delete(
        "/api/delete", params={"uid": uid, "media_id": media_id}
    )
    json_response = response.json()
    assert "status" in json_response
    assert "media_id" in json_response
    assert json_response["media_id"] == media_id
    assert json_response["status"] == ProgressStatusEnum.DELETED
    response = app_client.get("/api/info", params={"uid": uid})
    assert response.status_code == 200
    # deleted media file cannot be present in downloads
    assert media_id not in [
        d['media_id'] for d in response.json()["downloads"] if d["media_id"] == media_id
    ]
