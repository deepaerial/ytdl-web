from .downloaders import IDownloader
from .schemas.models import Download
from .schemas.requests import DownloadParams


def create_download_from_download_params(
    client_id: str, download_params: DownloadParams, downloader: IDownloader
) -> Download:
    """
    Function for creating Download object from DownloadParams.
    """
    video_info = downloader.get_video_info(download_params.url)
    download = Download(
        client_id=client_id,
        title=video_info.title,
        url=video_info.url,
        audio_streams=video_info.audio_streams,
        video_streams=video_info.video_streams,
        audio_stream_id=download_params.audio_stream_id,
        video_stream_id=download_params.video_stream_id,
        media_format=download_params.media_format,
        thumbnail_url=video_info.thumbnail_url,
        duration=video_info.duration,
    )
    return download
