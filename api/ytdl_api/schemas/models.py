from pathlib import Path
from typing import List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    PrivateAttr
)

from ..constants import MediaFormatOptions, ProgressStatusEnum
from ..types import DownloadDataInfo


class BaseStream(BaseModel):
    id: str = Field(..., description="Stream ID", example="123")
    mimetype: str = Field(..., description="Stream mime-type", example="audio/webm")


class VideoStream(BaseStream):
    resolution: str = Field(..., description="Video resolution", example="1080p")


class AudioStream(BaseStream):
    bitrate: str = Field(..., description="Audio average bitrate", example="160kbps")


class Download(BaseModel):
    media_id: str = Field(
        ..., description="Download id", example="1080c61c7683442e8d466c69917e8aa4"
    )
    title: str = Field(
        ...,
        description="Video title",
        example="Adam Knight - I've Got The Gold (Shoby Remix)",
    )
    url: Union[AnyHttpUrl, str] = Field(
        ...,
        description="URL of video",
        example="https://www.youtube.com/watch?v=B8WgNGN0IVA",
    )
    video_streams: List[VideoStream] = Field(
        ...,
        description="List of video streams",
        example=[VideoStream(id="133", resolution="240p", mimetype="video/mp4")],
    )
    audio_streams: List[AudioStream] = Field(
        ...,
        description="List of audio streams",
        example=[AudioStream(id="89", bitrate="128kbps", mimetype="audio/webm")],
    )
    video_stream_id: Optional[str] = Field(
        None, description="Video stream ID (downloaded)", example="133"
    )
    audio_stream_id: Optional[str] = Field(
        None, description="Audio stream ID (downloaded)", example="118"
    )
    media_format: MediaFormatOptions = Field(
        None, description="Video or audio (when extracting) format of file",
    )
    duration: int = Field(
        ..., description="Video duration (in milliseconds)", example=479000
    )
    filesize: int = Field(
        None, description="Video/audio filesize (in bytes)", example=5696217
    )
    thumbnail_url: Union[AnyHttpUrl, str] = Field(
        ...,
        description="Video thumbnail",
        example="https://i.ytimg.com/vi_webp/B8WgNGN0IVA/maxresdefault.webp",
    )
    status: ProgressStatusEnum = Field(
        None, description="Download status", example=ProgressStatusEnum.DOWNLOADING
    )
    _file_path: Optional[Path] = PrivateAttr(None)
    progress: int = Field(0, description="Download progress in %", example=20)

    @property
    def filename(self) -> str:
        """
        File name with extension
        """
        return f"{self.title}.{self.media_format}"

    @property
    def file_path(self) -> str:
        """
        POSIX File path
        """
        return self._file_path.absolute().as_posix()


class DownloadProgress(BaseModel):
    client_id: str = Field(..., description="Id of client")
    media_id: str = Field(..., description="Id of downloaded media")
    status: ProgressStatusEnum = Field(
        ..., description="Download status", example=ProgressStatusEnum.DOWNLOADING
    )
    progress: int = Field(..., description="Download progress of a file", example=10)

    @classmethod
    def from_youtube_dl_data(
        cls, client_id: str, media_id: str, data: DownloadDataInfo
    ) -> "DownloadProgress":
        status = data["status"]
        percentage = data.get("_percent_str")
        if percentage:
            progress_str = percentage.strip().replace("%", "")
        else:
            progress_str = 0
        progress = round(float(progress_str))
        return cls(
            media_id=media_id,
            client_id=client_id,
            status=status,
            progress=int(progress),
        )

    @classmethod
    def from_pytube_data(
        cls, client_id, media_id, stream, chunk, bytes_remaining
    ) -> "DownloadProgress":
        # TODO: implement on progress for pytube
        pass

    @classmethod
    def from_download(cls, client_id: str, download: Download):
        return cls(
            client_id=client_id,
            media_id=download.media_id,
            status=download.status,
            progress=download.progress,
        )
