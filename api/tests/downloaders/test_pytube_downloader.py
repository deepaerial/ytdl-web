import pytest
from ytdl_api.downloaders import PytubeDownloader

from ytdl_api.schemas import Download

@pytest.fixture
def pytube_downloader(fake_media_path, fake_db, task_queue):
    return PytubeDownloader(
        media_path=fake_media_path,
        datasource=fake_db,
        event_queue=NotificationQueue(DownloadersTypes.PYTUBE),
        task_queue=task_queue,
    )

def test_pytube_downloader_get_video_info(pytube_downloader: PytubeDownloader):
    """
    Testing downloader for fetching info data about video
    """
    url = "https://www.youtube.com/watch?v=rsd4FNGTRBw"
    download = pytube_downloader.get_video_info(url)
    assert isinstance(download, Download)
    assert download.media_id is not None


def test_pytube_downloader_download_video(pytube_downloader: PytubeDownloader):
    """
    Testing downloading video using pytube
    """
    url = "https://www.youtube.com/watch?v=rsd4FNGTRBw"
    download = pytube_downloader.get_video_info(url)
    download.video_stream_id = download.video_streams[0].id
    download.media_format = MediaFormatOptions.MP4
    pytube_downloader.download(download)
    # Check if file was downloaded
    assert download._file_path is not None
    assert download._file_path.exists()


def test_pytube_downloader_no_stream_provided(pytube_downloader: PytubeDownloader):
    """
    Testing if exception is raised when no video/audio stream provided for pytube downloader.
    """
    with pytest.raises(Exception):
        url = "https://www.youtube.com/watch?v=rsd4FNGTRBw"
        download = pytube_downloader.get_video_info(url)
        pytube_downloader.download(download)


def test_pytube_downloader_no_format_provided(pytube_downloader: PytubeDownloader):
    """
    Testing if exception is raised when no media_format provided for pytube downloader.
    """
    with pytest.raises(Exception):
        url = "https://www.youtube.com/watch?v=rsd4FNGTRBw"
        download = pytube_downloader.get_video_info(url)
        download.video_stream_id = download.video_streams[0].id
        pytube_downloader.download(download)
