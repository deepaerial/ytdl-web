import abc
from pathlib import Path

from deta import Deta
from .schemas.models import Download


class IStorage(abc.ABC):
    """
    Base interface for storage class that manages downloaded file.
    """

    @abc.abstractmethod
    def save_download(
        self, download: Download, data: bytes, path: str
    ) -> str:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def save_download_from_file(
        self, download: Download, path: str
    ) -> str:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def download_exists(self, path: str) -> bool:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def get_download(self, path: str) -> bytes:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def remove_download(self, path: str):  # pragma: no cover
        raise NotImplementedError


class LocalFileStorage(IStorage):
    """
    Storage that saves downloaded files to host's filesystem.
    """

    def __init__(self, downloads_dir: Path) -> None:
        self.dowloads_dir = downloads_dir

    def save_download(self, download: Download, data: bytes) -> str:
        return download.storage_filename

    def save_download_from_file(self, download: Download, path: str) -> str:
        return download.storage_filename

    def download_exists(self, path: str) -> bool:
        # TODO: finish implementation
        ...

    def get_download(self, path: str) -> bytes:
        # TODO: finish implementation
        ...

    def remove_download(self, path: str):
        # TODO: finish implementation
        ...


class DetaDriveStorage(IStorage):
    """
    Storage for saving downloaded media files in Deta Drive.
    """

    def __init__(self, deta_project_key: str, drive_name: str) -> None:
        deta = Deta(project_key=deta_project_key)
        self.drive = deta.Drive(drive_name)

    def save_download(self, download: Download, data: bytes) -> str:
        self.drive.put(download.storage_filename, data=data)
        return download.storage_filename

    def save_download_from_file(self, download: Download, path: str) -> str:
        self.drive.put(download.storage_filename, path=path)
        return download.storage_filename
