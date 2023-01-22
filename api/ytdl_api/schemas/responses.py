from typing import List

from pydantic import Field

from ..constants import DownloadStatus, MediaFormat
from ..types import VideoURL
from .base import BaseModel_
from .models import AudioStream, Download, VideoStream


class ErrorResponse(BaseModel_):
    detail: str = Field(..., description="Message detail")
    code: str = Field(..., description="Custom error identifying code")


class DownloadsResponse(BaseModel_):
    downloads: List[Download] = Field(
        ...,
        description="List of pending and finished downloads",
    )


class VersionResponse(BaseModel_):
    api_version: str


class DeleteResponse(BaseModel_):
    media_id: str = Field(..., description="Id of downloaded media")
    status: DownloadStatus = Field(..., description="Download status")


class VideoInfoResponse(BaseModel_):
    url: VideoURL = Field(..., title="URL", description="URL to video")
    title: str = Field(..., description="Video title")
    duration: int = Field(..., description="Video length in seconds")
    thumbnail_url: VideoURL = Field(..., description="Video thumbnail")
    audio_streams: List[AudioStream] = Field([], description="Available audio streams")
    video_streams: List[VideoStream] = Field([], description="Available video streams")
    media_formats: List[MediaFormat] = Field(
        list(MediaFormat), description="Available media formats"
    )
