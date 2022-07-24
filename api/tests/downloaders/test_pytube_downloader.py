import random
from typing import Generator
from pathlib import Path

import pytest

from ytdl_api.callbacks import (
    on_finish_callback,
    on_pytube_progress_callback,
    on_start_converting,
)
from ytdl_api.constants import MediaFormat
from ytdl_api.converters import create_download_from_download_params
from ytdl_api.datasource import IDataSource
from ytdl_api.downloaders import IDownloader, PytubeDownloader
from ytdl_api.queue import NotificationQueue
from ytdl_api.schemas.models import Download
from ytdl_api.schemas.requests import DownloadParams
from ytdl_api.schemas.responses import VideoInfoResponse


@pytest.fixture
def pytube_downloader(fake_media_path: Path, mock_datasource: IDataSource):
    return PytubeDownloader(
        media_path=fake_media_path,
        datasource=mock_datasource,
        event_queue=NotificationQueue(),
    )


@pytest.fixture
def video_info(mock_url: str, pytube_downloader: PytubeDownloader) -> VideoInfoResponse:
    review = pytube_downloader.get_video_info(mock_url)
    return review


@pytest.fixture()
def mock_download_params(
    mock_url: str, video_info: VideoInfoResponse
) -> DownloadParams:
    video_stream_id = random.choice(video_info.video_streams).id
    audio_stream_id = random.choice(video_info.audio_streams).id
    return DownloadParams(
        url=mock_url,
        video_stream_id=video_stream_id,
        audio_stream_id=audio_stream_id,
        media_format=MediaFormat.MP4,
    )


@pytest.fixture()
def mock_persisted_download(
    uid: str,
    mock_download_params: DownloadParams,
    mock_datasource: IDataSource,
    pytube_downloader: IDownloader,
) -> Generator[Download, None, None]:
    mock_download = create_download_from_download_params(
        uid, mock_download_params, pytube_downloader
    )
    mock_datasource.put_download(mock_download)
    yield mock_download


def test_pytube_downloader_get_video_info(video_info):
    """
    Testing downloader for fetching info data about video
    """
    assert isinstance(video_info, VideoInfoResponse)
    assert video_info.title is not None
    assert video_info.thumbnail_url is not None
    assert video_info.audio_streams is not None
    assert video_info.video_streams is not None
    assert isinstance(video_info.media_formats, list)


def test_pytube_downloader_download_video(
    pytube_downloader: PytubeDownloader,
    mock_persisted_download: Download,
    mock_datasource: IDataSource,
):
    """
    Testing downloading video using pytube
    """
    pytube_downloader.download(
        mock_persisted_download,
        on_pytube_progress_callback,
        on_start_converting,
        on_finish_callback,
    )
    # Check if file was downloaded
    download = mock_datasource.get_download(
        mock_persisted_download.client_id, mock_persisted_download.media_id
    )
    assert download.status == "finished"
    assert download.file_path is not None
    assert download.file_path.exists()
