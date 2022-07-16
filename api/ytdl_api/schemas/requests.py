import re
from typing import Optional

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    validator,
    root_validator,
)
from ..constants import MediaFormatOptions, YOUTUBE_URI_REGEX


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
        ..., description="Video or audio (when extracting) format of file",
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
        url_patterns = (YOUTUBE_URI_REGEX,)
        if not any(re.compile(p).match(url) for p in url_patterns):
            raise ValueError("Domain is not allowed")
        return url