import abc
from typing import Optional
from pathlib import Path
import shutil

from deta import Deta
from .schemas.models import Download


class IStorage(abc.ABC):
    """
    Base interface for storage class that manages downloaded file.
    """

    @abc.abstractmethod
    def save_download(self, download: Download, data: bytes) -> str:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def save_download_from_file(
        self, download: Download, path: Path
    ) -> str:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def get_download(
        self, storage_file_name: str
    ) -> Optional[bytes]:  # pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def remove_download(self, storage_file_name: str):  # pragma: no cover
        raise NotImplementedError


class LocalFileStorage(IStorage):
    """
    Storage that saves downloaded files to host's filesystem.
    """

    def __init__(self, downloads_dir: Path) -> None:
        self.dowloads_dir = downloads_dir

    def save_download(self, download: Download, data: bytes) -> str:
        storage_file_path = self.dowloads_dir / download.storage_filename
        with storage_file_path.open("+wb") as f:
            f.write(data)
        return storage_file_path.as_posix()

    def save_download_from_file(self, download: Download, path: Path) -> str:
        dest_path = self.dowloads_dir / download.storage_filename
        shutil.copy(path, dest_path)
        return dest_path.as_posix()

    def get_download(self, storage_file_name: str) -> Optional[bytes]:
        download_file = Path(storage_file_name)
        if not download_file.exists():
            return None
        return download_file.read_bytes()

    def remove_download(self, storage_file_name: str):
        download_file = Path(storage_file_name)
        if download_file.exists():
            download_file.unlink()


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

    def save_download_from_file(self, download: Download, path: Path) -> str:
        self.drive.put(download.storage_filename, path=path)
        return download.storage_filename
