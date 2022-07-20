from typing import List

from pydantic import BaseModel, Field

from ..constants import MediaFormat, ProgressStatusEnum
from ..types import VideoURL
from .models import AudioStream, Download, VideoStream


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Message detail")
    code: str = Field(..., description="Custom error identifying code")


class DownloadsResponse(BaseModel):
    downloads: List[Download] = Field(
        ..., description="List of pending and finished downloads",
    )


class VersionResponse(BaseModel):
    api_version: str


class DeleteResponse(BaseModel):
    media_id: str = Field(..., description="Id of downloaded media")
    status: ProgressStatusEnum = Field(..., description="Download status")


class VideoInfoResponse(BaseModel):
    url: VideoURL = Field(..., title="URL", description="URL to video")
    title: str = Field(..., description="Video title")
    duration: int = Field(..., description="Video length in seconds")
    thumbnail_url: VideoURL = Field(..., description="Video thumbnail")
    audio_streams: List[AudioStream] = Field([], description="Available audio streams")
    video_streams: List[VideoStream] = Field([], description="Available video streams")
    media_formats: List[MediaFormat] = Field(
        list(MediaFormat), description="Available media formats"
    )
