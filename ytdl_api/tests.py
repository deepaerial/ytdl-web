from fastapi.testclient import TestClient

from .asgi import app

client = TestClient(app)


def test_session_endpoint():
    """
    Test endpoint that initializes session for client (both authorized and non-authorized)
    """
    response = client.get("/api/check")
    assert response.status_code == 200
    assert "downloads" in response.json()


def test_version_endpoint():
    """
    Test endpoint that returns information about API version.
    """
    response = client.get("/api/version")
    assert response.status_code == 200
    assert "api_version" in response.json()
    assert "youtube_dl_version" in response.json()


def test_dowload_endpoint_no_format():
    """
    Test enpoint for downloading video.

    Verify that error raised when no format is passed in POST body.
    """
    response = client.put(
        "/api/fetch",
        json={"params": {"urls": ["https://www.youtube.com/watch?v=0ruMGbPXxbA"]}},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_dowload_endpoint_video():
    """
    Test enpoint for downloading video.

    Verify that video dowload works
    """
    response = client.put(
        "/api/fetch",
        json={
            "urls": ["https://www.youtube.com/watch?v=0ruMGbPXxbA"],
            "media_format": "mp4",
        },
    )
    assert response.status_code == 201
    assert "downloads" in response.json()


def test_dowload_endpoint_audio():
    """
    Test enpoint for downloading video.

    Verify that audio dowload works
    """
    response = client.put(
        "/api/fetch",
        json={
            "urls": ["https://www.youtube.com/watch?v=0ruMGbPXxbA"],
            "media_format": "mp3",
        },
    )
    assert response.status_code == 201
    assert "downloads" in response.json()
