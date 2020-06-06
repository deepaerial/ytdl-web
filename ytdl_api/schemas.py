from enum import Enum
from typing import List
from pydantic import BaseModel, AnyHttpUrl, Field, root_validator


class DefaultErrorResponse(BaseModel):
    detail: str = Field(
        ..., description="Error detail message", example="Internal Server Error"
    )


class NoValidSessionError(DefaultErrorResponse):
    detail: str = Field(..., example="No valid session")


class VersionResponse(BaseModel):
    youtube_dl_version: str = Field(..., example="2020.03.24")
    api_version: str = Field(..., example="0.1.0")


class InfoResponse(BaseModel):
    video_url: str = Field(
        ...,
        description="URL of video",
        example="https://www.youtube.com/watch?v=B8WgNGN0IVA",
    )
    thumbnail_url: AnyHttpUrl = Field(
        ...,
        description="Link to video thumbnail",
        example="https://img.youtube.com/vi/B8WgNGN0IVA/0.jpg",
    )


class StatusResponse(BaseModel):
    status: str = Field("OK", description="Error detail message", example="OK")


class ExceptionSchema(BaseModel):
    detail: str


class AudioFormatOptions(str, Enum):
    BEST = "best"  # allow youtube-dl automatically decide which one to use
    AAC = "aac"
    FLAC = "flac"
    MP3 = "mp3"
    M4A = "m4a"
    OPUS = "opus"
    VORBIS = "vorbis"
    WAV = "wav"


class VideoFormatOptions(str, Enum):
    MP4 = "mp4"
    FLV = "flv"
    WEBM = "webm"
    OGG = "ogg"
    MKV = "mkv"
    AVI = "avi"


class YTDLParams(BaseModel):
    urls: List[AnyHttpUrl] = Field(
        ...,
        title="URLs",
        description="URLs to videos",
        example=["https://www.youtube.com/watch?v=B8WgNGN0IVA"],
    )
    audio_format: AudioFormatOptions = Field(
        None, description="Audio format of file (needed only if extracting audio)",
    )
    video_format: VideoFormatOptions = Field(
        None, description="Video extension/format of file"
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

    @root_validator(pre=True)
    def validate_format(cls, values):
        audio_f, video_f = values.get("audio_format"), values.get("video_format")
        if not any([audio_f, video_f]):
            raise ValueError("At least on format type is required")
        return values


class DownloadParamsModel(BaseModel):
    params: YTDLParams = Field(
        ..., title="Download params", description="Youtube-dl download params"
    )

    class Config:
        validate_all = True
