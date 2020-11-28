import typing


class DownloadDataInfo(typing.TypedDict):
    status: str
    filename: str
    tmpfilename: str
    downloaded_bytes: int
    total_bytes: typing.Union[None, int]
    total_bytes_estimate: int
    elapsed: int
    eta: typing.Union[int, None]
    speed: typing.Union[int, None]
    fragment_index: int
    fragment_count: int
