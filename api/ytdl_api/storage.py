import abc
from pathlib import Path


class IStorage(abc.ABC):
    """
    Base interface for storage class that manages downloaded file.
    """

    @abc.abstractmethod
    def save_download(self, data: bytes, path: str) -> str:
        raise NotImplementedError
    
    @abc.abstractmethod
    def download_exists(self, path: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_download(self, path: str)) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def remove_download(self, path: str)):
        raise NotImplementedError


class LocalFileStorage(IStorage):
    """
    Storage that saves downloaded files to host's filesystem.
    """

    def __init__(self, downloads_dir: Path) -> None:
        self.dowloads_dir = downloads_dir

    def save_download(self, data: bytes, path: str) -> str:
        # TODO: finish implementation
        ...

    def download_exists(self, path: str) -> bool:
        # TODO: finish implementation
        ...

    def get_download(self, path: str) -> bytes:
        # TODO: finish implementation
        ...

    def remove_download(self, path: str):
        # TODO: finish implementation
        ...
