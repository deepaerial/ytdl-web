from pathlib import Path
from fastapi.testclient import TestClient
from .dependencies import get_database, get_settings
from .downloaders import get_unique_id
from .config import Settings, DbTypes

settings = Settings(
    media_path=Path(__file__).parent.parent / "media", db_type=DbTypes.MEMORY, allow_origins=[]
)

app = settings.init_app()
client = TestClient(app)

app.dependency_overrides[get_settings] = lambda: settings


def test_version_endpoint():
    """
    Test endpoint that returns information about API version.
    """
    response = client.get("/api/info")
    assert response.status_code == 200
    assert "api_version" in response.json()
    assert "youtube_dl_version" in response.json()


def test_download_endpoint_no_format():
    """
    Test endpoint for starting video download task.

    Verify that error raised when no format is passed in POST body.
    """
    response = client.put(
        "/api/fetch",
        params={"uid": get_unique_id()},
        json={"url": "https://www.youtube.com/watch?v=0ruMGbPXxbA"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_download_endpoint_bad_url():
    """
    Test endpoint for starting video download task.

    Verify that error raised when unsupported url is passed in POST body.
    """
    response = client.put(
        "/api/fetch",
        params={"uid": get_unique_id()},
        json={"url": "https://www.notube.com/watch?v=0ruMGbPXxbA"},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_download_endpoint_video():
    """
    Test endpoint for starting video download task.

    Verify that video dowload works
    """
    response = client.put(
        "/api/fetch",
        params={"uid": get_unique_id()},
        json={
            "url": "https://www.youtube.com/watch?v=0ruMGbPXxbA",
            "media_format": "mp4",
        },
    )
    assert response.status_code == 201
    assert "downloads" in response.json()


def test_download_endpoint_audio():
    """
    Test endpoint for starting audio download task.

    Verify that audio dowload works
    """
    response = client.put(
        "/api/fetch",
        params={"uid": get_unique_id()},
        json={
            "url": "https://www.youtube.com/watch?v=0ruMGbPXxbA",
            "media_format": "mp3",
        },
    )
    assert response.status_code == 201
    assert "downloads" in response.json()


def test_download_fetched_media():
    """
    Test endpoint for fetching downloaded media.
    """
    uid = get_unique_id()
    response = client.put(
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
    response = client.get(
        "/api/fetch", params={"uid": uid, "media_id": download["media_id"]}
    )
    assert response.status_code == 200
