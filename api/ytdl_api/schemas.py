import re
from enum import Enum
from pathlib import Path
from typing import List, Optional, TypedDict, Union

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    PrivateAttr,
    validator,
    root_validator,
)


class DetailMessage(BaseModel):
    detail: str = Field(
        ..., description="Message detail", example="Internal server error"
    )
    code: str = Field(description="Custom error identifying code")


class MediaFormatOptions(str, Enum):
    # Video formats
    MP4 = "mp4"
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"

    @property
    def is_audio(self) -> bool:
        return self.name in [MediaFormatOptions.MP3, MediaFormatOptions.WAV]


class ProgressStatusEnum(str, Enum):
    STARTED = "started"
    DOWNLOADING = "downloading"
    FINISHED = "finished"
    DOWNLOADED = "downloaded"  # by client
    DELETED = "deleted"


# TODO: remove due to deprecation
class ThumbnailInfo(BaseModel):
    url: AnyHttpUrl = Field(
        ...,
        description="Link to video thumbnail",
        example="https://img.youtube.com/vi/B8WgNGN0IVA/0.jpg",
    )
    width: int = Field(
        ..., description="Thumbnail width", example=246,
    )
    height: int = Field(
        ..., description="Thumbnail height", example=138,
    )


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
    url: AnyHttpUrl = Field(
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
    thumbnail_url: AnyHttpUrl = Field(
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


class FetchedListResponse(BaseModel):
    downloads: List[Download] = Field(
        ...,
        description="List of pending and finished downloads",
        example=[
            {
                "media_id": "1080c61c7683442e8d466c69917e8aa4",
                "title": "Adam Knight - I've Got The Gold (Shoby Remix)",
                "url": "https://www.youtube.com/watch?v=B8WgNGN0IVA",
                "streams": [
                    VideoStream(id="134", resolution="720p", mimetype="video/mp4"),
                    AudioStream(id="114", bitrate="128kbps", mimetype="audio/mp4"),
                ],
                "duration": 231000,
                "status": ProgressStatusEnum.STARTED,
                "thumbnail_url": "https://i.ytimg.com/vi_webp/B8WgNGN0IVA/maxresdefault.webp",
                "progress": 0,
            }
        ],
    )


class VersionResponse(BaseModel):
    api_version: str = Field(..., example="0.1.0")
    media_options: List[MediaFormatOptions] = Field(
        ...,
        description="List of available media options for download",
        example=[media_format.value for media_format in MediaFormatOptions],
    )
    uid: str = Field(
        ...,
        description="Unique session identifier",
        example="1080c61c7683442e8d466c69917e8aa4",
    )
    downloads: List[Download] = Field(
        ...,
        description="List of pending and finished downloads",
        example=[
            {
                "media_id": "1080c61c7683442e8d466c69917e8aa4",
                "title": "Adam Knight - I've Got The Gold (Shoby Remix)",
                "url": "https://www.youtube.com/watch?v=B8WgNGN0IVA",
                "duration": 231000,
                "filesize": None,
                "status": ProgressStatusEnum.DOWNLOADING,
                "thumbnail": {
                    "url": "https://i.ytimg.com/vi_webp/B8WgNGN0IVA/maxresdefault.webp",
                    "width": 1920,
                    "height": 1080,
                },
                "progress": 57,
            }
        ],
    )


class YTDLParams(BaseModel):
    url: AnyHttpUrl = Field(
        ...,
        title="URL",
        description="URL to video",
        example="https://www.youtube.com/watch?v=B8WgNGN0IVA",
    )
    video_stream_id: Optional[str] = Field(
        None, description="Video stream ID", example="133"
    )
    audio_stream_id: Optional[str] = Field(
        None, description="Audio stream ID", example="118"
    )
    media_format: MediaFormatOptions = Field(
        ...,
        description="Video or audio (when extracting) format of file",
    )

    class Config:
        validate_all = True

    @root_validator
    def validate_stream_ids(cls, values):
        video_stream_id, audio_stream_id = (
            values.get("video_stream_id"),
            values.get("audio_stream_id"),
        )
        if not any((video_stream_id, audio_stream_id)):
            raise ValueError(
                "Video or/and audio stream id should be specified for download."
            )
        return values

    @validator("url")
    def is_url_allowed(cls, url):
        url_patterns = (
            r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$",
        )
        if not any(re.compile(p).match(url) for p in url_patterns):
            raise ValueError("Domain is not allowed")
        return url


class DownloadDataInfo(TypedDict):
    _eta_str: Optional[str]
    _percent_str: Optional[str]
    _speed_str: Optional[str]
    _total_bytes_str: Optional[str]
    status: str
    filename: str
    tmpfilename: str
    downloaded_bytes: int
    total_bytes: int
    total_bytes_estimate: Optional[int]
    elapsed: int
    eta: Optional[int]
    speed: Optional[int]
    fragment_index: Optional[int]
    fragment_count: Optional[int]


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

    @classmethod
    def from_download(cls, client_id: str, download: Download):
        return cls(
            client_id=client_id,
            media_id=download.media_id,
            status=download.status,
            progress=download.progress,
        )


class DeleteResponse(BaseModel):
    media_id: str = Field(..., description="Id of downloaded media")
    status: ProgressStatusEnum = Field(
        ..., description="Download status", example=ProgressStatusEnum.DELETED
    )
