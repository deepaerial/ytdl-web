import datetime
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, Field

from ..constants import DownloadStatus, MediaFormat
from ..types import VideoURL
from .base import BaseModel_
from .models import AudioStream, VideoStream


class ErrorResponse(BaseModel_):
    detail: str = Field(..., description="Message detail")
    code: str = Field(..., description="Custom error identifying code")


class DownloadResponse(BaseModel_):
    client_id: str = Field(..., description="Client ID")
    media_id: str = Field(..., description="Download id")
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


class DownloadsResponse(BaseModel_):
    downloads: List[DownloadResponse] = Field(
        ...,
        description="List of pending and finished downloads",
    )


class VersionResponse(BaseModel_):
    api_version: str


class DeleteResponse(BaseModel_):
    media_id: str = Field(..., description="Id of downloaded media")
    status: DownloadStatus = Field(..., description="Download status")
    isAudio: bool = Field(..., description="Is deleted file was audio file")
    title: str = Field(..., description="Deleted media file title")


class VideoInfoResponse(BaseModel_):
    url: VideoURL = Field(..., title="URL", description="URL to video")
    title: str = Field(..., description="Video title")
    duration: int = Field(..., description="Video length in seconds")
    thumbnail_url: AnyHttpUrl = Field(..., description="Video thumbnail")
    audio_streams: List[AudioStream] = Field([], description="Available audio streams")
    video_streams: List[VideoStream] = Field([], description="Available video streams")
    media_formats: List[MediaFormat] = Field(
        list(MediaFormat), description="Available media formats"
    )
