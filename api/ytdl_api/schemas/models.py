from pathlib import Path
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Field

from ..constants import DonwloadStatus, MediaFormat
from ..types import VideoURL
from ..utils import get_unique_id


class BaseStream(BaseModel):
    id: str = Field(..., description="Stream ID", example="123")
    mimetype: str = Field(..., description="Stream mime-type", example="audio/webm")


class VideoStream(BaseStream):
    resolution: str = Field(..., description="Video resolution", example="1080p")


class AudioStream(BaseStream):
    bitrate: str = Field(..., description="Audio average bitrate", example="160kbps")


class Download(BaseModel):
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
    status: DonwloadStatus = Field(
        DonwloadStatus.STARTED, description="Download status"
    )
    file_path: Optional[Path] = Field(None, description="Path to file")
    progress: int = Field(0, description="Download progress in %")

    @property
    def filename(self) -> str:
        """
        File name with extension
        """
        return f"{self.title}.{self.media_format}"


class DownloadProgress(BaseModel):
    client_id: str = Field(..., description="Id of client")
    media_id: str = Field(..., description="Id of downloaded media")
    status: DonwloadStatus = Field(
        ..., description="Download status", example=DonwloadStatus.DOWNLOADING
    )
    progress: int = Field(..., description="Download progress of a file", example=10)
