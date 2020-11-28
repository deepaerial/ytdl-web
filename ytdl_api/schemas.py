from enum import Enum
from typing import List
from pydantic import BaseModel, AnyHttpUrl, Field

from . import types


class DefaultErrorResponse(BaseModel):
    detail: str = Field(
        ..., description="Error detail message", example="Internal Server Error"
    )


class NoValidSessionError(DefaultErrorResponse):
    detail: str = Field(..., example="No valid session")


class ExceptionSchema(BaseModel):
    detail: str


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


class YTDLParams(BaseModel):
    urls: List[AnyHttpUrl] = Field(
        ...,
        title="URLs",
        description="URLs to videos",
        example=["https://www.youtube.com/watch?v=B8WgNGN0IVA"],
    )
    media_format: MediaFormatOptions = Field(
        ..., description="Video or audio (when extracting) format of file",
    )
    use_last_modified: bool = Field(
        False,
        title="Last-modified header",
        description="Use the Last-modified header to set the file modification time",
    )
    outtmpl: str = Field(
        "%(title)s.%(ext)s",
        title="Output format",
        description="Output template https://github.com/ytdl-org/youtube-dl#output-template",
    )

    class Config:
        validate_all = True


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


class FetchedItem(BaseModel):
    title: str = Field(
        ...,
        description="Video title",
        example="Adam Knight - I've Got The Gold (Shoby Remix)",
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


class FetchedListResponse(BaseModel):
    downloads: List[FetchedItem] = Field(
        ...,
        description="List of pending and finished downloads",
        example=[
            {
                "title": "Adam Knight - I've Got The Gold (Shoby Remix)",
                "duration": 231000,
                "filesize": None,
                "video_url": "https://www.youtube.com/watch?v=B8WgNGN0IVA",
                "thumbnail": {
                    "url": "https://i.ytimg.com/vi_webp/B8WgNGN0IVA/maxresdefault.webp",
                    "width": 1920,
                    "height": 1080,
                },
            }
        ],
    )


class DownloadProgress(BaseModel):
    media_id: str = Field(..., description="Id of downloaded media")
    status: str = Field(..., description="Download status")
    progress: int = Field(..., description="Download progress of a file")

    @classmethod
    def from_data(cls, media_id: str, data: types.DownloadDataInfo) -> 'DownloadProgress':
        status = data['status']
        progress_str = data['_percent_str'].strip().replace("%", "") 
        progress = round(float(progress_str))
        return cls(media_id=media_id, status=status, progress=progress)
