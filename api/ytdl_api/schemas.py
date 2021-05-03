import re
from enum import Enum
from pathlib import Path
from typing import List, Optional, TypedDict, Union
from starlette.responses import FileResponse

from pydantic import AnyHttpUrl, BaseModel, Field, PrivateAttr, validator

from .logger import YDLLogger


class DetailMessage(BaseModel):
    detail: str = Field(
        ..., description="Message detail", example="Internal server error"
    )
    code: str = Field(description="Custom error identifying code")


class MediaFormatOptions(str, Enum):
    # Video formats
    MP4 = "mp4"
    FLV = "flv"
    WEBM = "webm"
    OGG = "ogg"
    MKV = "mkv"
    AVI = "avi"

    # Audio formats
    AAC = "aac"
    FLAC = "flac"
    MP3 = "mp3"
    M4A = "m4a"
    OPUS = "opus"
    VORBIS = "vorbis"
    WAV = "wav"

    @property
    def is_audio(self) -> bool:
        return self.name in [
            "best",
            "aac",
            "flac",
            "mp3",
            "m4a",
            "opus",
            "vorbis",
            "wav",
        ]


class ProgressStatusEnum(str, Enum):
    STARTED = "stated"
    DOWNLOADING = "downloading"
    FINISHED = "finished"


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


class Download(BaseModel):
    title: str = Field(
        ...,
        description="Video title",
        example="Adam Knight - I've Got The Gold (Shoby Remix)",
    )
    media_format: MediaFormatOptions = Field(
        ..., description="Video or audio (when extracting) format of file",
    )
    duration: int = Field(
        ..., description="Video duration (in milliseconds)", example=479000
    )
    filesize: int = Field(
        None, description="Video/audio filesize (in bytes)", example=5696217
    )
    video_url: AnyHttpUrl = Field(
        ...,
        description="URL of video",
        example="https://www.youtube.com/watch?v=B8WgNGN0IVA",
    )
    thumbnail: ThumbnailInfo = Field(
        ...,
        description="Video thumbnail",
        example={
            "url": "https://i.ytimg.com/vi_webp/B8WgNGN0IVA/maxresdefault.webp",
            "width": 1920,
            "height": 1080,
        },
    )
    status: ProgressStatusEnum = Field(
        None, description="Download status", example=ProgressStatusEnum.DOWNLOADING
    )
    media_id: str = Field(
        ..., description="Download id", example="1080c61c7683442e8d466c69917e8aa4"
    )
    _file_path: Optional[Path] = PrivateAttr(None)
    progress: int = Field(0, description="Download progress in ", example=20)


    @property
    def filename(self) -> str:
        '''
        File name with extension
        '''
        return f"{self.title}.{self.media_format}"

    @property
    def file_path(self) -> str:
        '''
        POSIX File path
        '''
        return self._file_path.absolute().as_posix()


class FetchedListResponse(BaseModel):
    downloads: List[Download] = Field(
        ...,
        description="List of pending and finished downloads",
        example=[
            {
                "title": "Adam Knight - I've Got The Gold (Shoby Remix)",
                "duration": 231000,
                "filesize": None,
                "video_url": "https://www.youtube.com/watch?v=B8WgNGN0IVA",
                "media_id": "1080c61c7683442e8d466c69917e8aa4",
                "status": "started",
                "thumbnail": {
                    "url": "https://i.ytimg.com/vi_webp/B8WgNGN0IVA/maxresdefault.webp",
                    "width": 1920,
                    "height": 1080,
                },
                "progress": 0,
            }
        ],
    )


class VersionResponse(BaseModel):
    youtube_dl_version: str = Field(..., example="2020.03.24")
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
                "title": "Adam Knight - I've Got The Gold (Shoby Remix)",
                "duration": 231000,
                "filesize": None,
                "video_url": "https://www.youtube.com/watch?v=B8WgNGN0IVA",
                "media_id": "1080c61c7683442e8d466c69917e8aa4",
                "status": "started",
                "thumbnail": {
                    "url": "https://i.ytimg.com/vi_webp/B8WgNGN0IVA/maxresdefault.webp",
                    "width": 1920,
                    "height": 1080,
                },
                "progress": 0,
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
    media_format: MediaFormatOptions = Field(
        ..., description="Video or audio (when extracting) format of file",
    )
    use_last_modified: bool = Field(
        False,
        title="Last-modified header",
        description="Use the Last-modified header to set the file modification time",
    )

    class Config:
        validate_all = True

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
    def from_data(
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

