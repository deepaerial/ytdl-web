from typing import Optional, TypedDict, Union, Callable, Coroutine, Any
from pydantic import AnyHttpUrl


URL = Union[AnyHttpUrl, str]
OnDownloadProgressCallback = Callable[..., Coroutine[Any, Any, Any]]


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
