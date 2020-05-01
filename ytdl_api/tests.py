from fastapi.testclient import TestClient

from .asgi import app

client = TestClient(app)


def test_version_endpoint():
    """
    Test endpoint that returns information about API version.
    """
    response = client.get("/api/version")
    assert response.status_code == 200
    assert "api_version" in response.json()


def test_dowload_endpoint_no_format():
    """
    Test enpoint for downloading video.

    Verify that error raised when no format is passed in POST body.
    """
    response = client.post(
        "/api/download",
        json={"params": {"urls": ["https://www.youtube.com/watch?v=0ruMGbPXxbA"]}},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_dowload_endpoint_video():
    """
    Test enpoint for downloading video.

    Verify that video dowload works
    """
    response = client.post(
        "/api/download",
        json={
            "params": {
                "urls": ["https://www.youtube.com/watch?v=0ruMGbPXxbA"],
                "video_format": "mp4",
            },
        },
    )
    assert response.status_code == 200
    assert "status" in response.json()


def test_dowload_endpoint_audio():
    """
    Test enpoint for downloading video.

    Verify that audio dowload works
    """
    response = client.post(
        "/api/download",
        json={
            "params": {
                "urls": ["https://www.youtube.com/watch?v=0ruMGbPXxbA"],
                "audio_format": "mp3",
            },
        },
    )
    assert response.status_code == 200
    assert "status" in response.json()
