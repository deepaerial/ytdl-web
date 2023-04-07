import re
from typing import Any, Callable, Coroutine, Optional, TypedDict

from pydantic import AnyHttpUrl

YOUTUBE_REGEX = re.compile(
    r"^((https?)?:(\/\/))?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
)


class VideoURL(AnyHttpUrl, str):
    """
    Custom type for Youtube video video URL.
    """

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(
            # simplified regex here for brevity, see the wikipedia link above
            pattern=YOUTUBE_REGEX.pattern,
        )

    @classmethod
    def validate(cls, v):
        match = YOUTUBE_REGEX.fullmatch(v)
        if not match:
            raise ValueError("Bad youtube video link provided.")
        full_url = match.group(0)
        scheme = match.group(2)
        return cls(url=full_url, scheme=scheme)


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
