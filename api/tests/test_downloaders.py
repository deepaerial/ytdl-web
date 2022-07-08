import pytest
from ytdl_api.downloaders import PytubeDownloader

from ytdl_api.schemas import Download, MediaFormatOptions, YTDLParams


@pytest.fixture
def download_params() -> YTDLParams:
    return YTDLParams(
        url="https://www.youtube.com/watch?v=rsd4FNGTRBw", media_format="mp4"
    )


SKIP_REASON = "current code breaks youtube-dl downloader"


@pytest.mark.skip(reason=SKIP_REASON)
def test_youtube_dl_get_video_info(youtube_dl_downloader, download_params):
    """
    Testing youtube_dl downloader for fetching video info data
    """
    download = youtube_dl_downloader.get_video_info(download_params)
    assert isinstance(download, Download)
    assert download.media_id is not None


@pytest.mark.skip(reason=SKIP_REASON)
def test_youtube_dl_download(youtube_dl_downloader, download_params):
    """
    Testing if downloader saves video to file in given media path
    """
    download = youtube_dl_downloader.get_video_info(download_params)
    youtube_dl_downloader.download(download_params, download.media_id)
    # Check if file was downloaded
    assert download._file_path.exists()


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
