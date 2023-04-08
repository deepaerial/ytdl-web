import datetime
from pathlib import Path
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, Field

from ..constants import DownloadStatus, MediaFormat
from ..types import VideoURL
from ..utils import get_unique_id
from .base import BaseModel_


class BaseStream(BaseModel_):
    id: str = Field(..., description="Stream ID", example="123")
    mimetype: str = Field(..., description="Stream mime-type", example="audio/webm")


class VideoStream(BaseStream):
    resolution: str = Field(..., description="Video resolution", example="1080p")


class AudioStream(BaseStream):
    bitrate: str = Field(..., description="Audio average bitrate", example="160kbps")


class Download(BaseModel_):
    client_id: str = Field(..., description="Client ID")
    media_id: str = Field(description="Download id", default_factory=get_unique_id)
    title: str = Field(..., description="Video title")
    url: VideoURL = Field(..., description="URL of video")
    video_streams: List[VideoStream] = Field(
        description="List of video streams", default_factory=list
    )
    audio_streams: List[AudioStream] = Field(
        description="List of audio streams", default_factory=list
    )
    video_stream_id: Optional[str] = Field(
        None, description="Video stream ID (downloaded)"
    )
    audio_stream_id: Optional[str] = Field(
        None, description="Audio stream ID (downloaded)"
    )
    media_format: MediaFormat = Field(
        None,
        description="Video or audio (when extracting) format of file",
    )
    duration: int = Field(..., description="Video duration (in milliseconds)")
    filesize: int = Field(None, description="Video/audio filesize (in bytes)")
    thumbnail_url: Union[AnyHttpUrl, str] = Field(..., description="Video thumbnail")
    status: DownloadStatus = Field(
        DownloadStatus.STARTED, description="Download status"
    )
    file_path: Optional[str] = Field(None, description="Path to file")
    progress: int = Field(0, description="Download progress in %")
    when_submitted: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        description="Date & time in UTC when download was submitted to API.",
    )
    when_started_download: Optional[datetime.datetime] = Field(
        None, description="Date & time in UTC when download started."
    )
    when_download_finished: Optional[datetime.datetime] = Field(
        None, description="Date & time in UTC when download finished."
    )
    when_file_downloaded: Optional[datetime.datetime] = Field(
        None, description="Date & time in UTC when file was downloaded."
    )
    when_deleted: Optional[datetime.datetime] = Field(
        None, description="Date & time in UTC when download was soft-deleted."
    )

    @property
    def storage_filename(self) -> str:
        """
        File name used when storing download in file storage.
        """
        return f"{self.media_id}.{self.media_format}"

    @property
    def filename(self) -> str:
        """
        File name with extension
        """
        return f"{self.title}.{self.media_format}"


class DownloadProgress(BaseModel_):
    client_id: str = Field(..., description="Id of client")
    media_id: str = Field(..., description="Id of downloaded media")
    status: DownloadStatus = Field(
        ..., description="Download status", example=DownloadStatus.DOWNLOADING
    )
    progress: int = Field(..., description="Download progress of a file", example=10)
