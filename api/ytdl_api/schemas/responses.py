from typing import List, Dict, Any, Type, Optional
from pathlib import Path

from pydantic import Field, AnyHttpUrl

from ..constants import DownloadStatus, MediaFormat
from ..types import VideoURL
from .base import BaseModel_
from .models import AudioStream, Download, VideoStream


class ErrorResponse(BaseModel_):
    detail: str = Field(..., description="Message detail")
    code: str = Field(..., description="Custom error identifying code")


class DownloadResponse(Download):
    file_path: Optional[Path] = Field(..., exclude=True)

    class Config(BaseModel_.Config):
        @staticmethod
        def schema_extra(
            schema: Dict[str, Any], model: Type["DownloadResponse"]
        ) -> None:
            schema.get("properties", {}).pop("filePath", None)


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
