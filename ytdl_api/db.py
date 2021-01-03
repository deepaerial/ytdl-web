from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
import typing
import itertools

from deta import Deta
from pydantic import AnyHttpUrl, parse_obj_as

from .schemas import Download, MediaFormatOptions, DownloadProgress


class DAOInterface(ABC):
    """
    Abstract interface that provides abstract methods for accessing and manipulating data
    from database.
    """

    @abstractmethod
    def fetch_downloads(self, client_id: str) -> typing.List[Download]:
        """
        Abstract method that returns list of clients downloads from data source.
        """
        raise NotImplementedError

    @abstractmethod
    def put_download(self, client_id: str, download: Download):
        """
        Abstract method for inserting download instance to data source.
        """
        raise NotImplementedError

    @abstractmethod
    def get_download(self, client_id: str, media_id: str) -> typing.Optional[Download]:
        """
        Abstract method for fetching download instance from data source
        """
        raise NotImplementedError

    @abstractmethod
    def update_download_progress(self, progress_obj: DownloadProgress):
        """
        Abstract method that updates progress for media item of specific user/client.
        """
        raise NotImplementedError

    @abstractmethod
    def get_download_if_exists(
        self, url: AnyHttpUrl, media_format: MediaFormatOptions
    ) -> typing.Optional[Download]:
        """
        Abstract method that returns True if media with given url and media format exists
        in downloaded media database.
        """
        raise NotImplementedError


class InMemoryDB(DAOInterface):
    """
    In-memory database implementation for DAOInterface.
    """

    storage: typing.DefaultDict[str, typing.List[Download]] = defaultdict(list)

    def fetch_downloads(self, client_id: str) -> typing.List[Download]:
        return self.storage[client_id] or []

    def put_download(self, client_id: str, download: Download):
        self.storage[client_id].append(download)

    def get_download(self, client_id: str, media_id: str) -> typing.Optional[Download]:
        return next(
            filter(lambda d: d.media_id == media_id, self.storage[client_id]), None,
        )

    def update_download_progress(self, progress_obj: DownloadProgress):
        download = self.get_download(progress_obj.client_id, progress_obj.media_id)
        download.progress = progress_obj.progress
        download.status = progress_obj.status

    def get_download_if_exists(
        self, url: AnyHttpUrl, media_format: MediaFormatOptions
    ) -> typing.Optional[Download]:
        downloads = list(itertools.chain.from_iterable(self.storage.values()))
        return next(
            filter(
                lambda d: d.video_url == url and d.media_format == media_format,
                downloads,
            ),
            None,
        )


class DetaDB(DAOInterface):
    """
    DAO interface implementation for Deta Bases: https://docs.deta.sh/docs/base/sdk
    """

    __base_name = "ytdl"

    def __init__(self, deta_project_key: str, base_name: typing.Optional[str] = None):
        deta = Deta(deta_project_key)
        if base_name:
            self.base = deta.Base(base_name)
        else:
            self.base = deta.Base(self.__base_name)

    def fetch_downloads(self, client_id: str) -> typing.List[Download]:
        downloads = next(self.base.fetch({"client_id": client_id}))
        return parse_obj_as(typing.List[Download], downloads)

    def put_download(self, client_id: str, download: Download):
        data = download.dict()
        data["client_id"] = client_id
        data["_file_path"] = download._file_path.absolute().as_posix()
        key = data["media_id"]

        self.base.put(data, key)

    def get_download(self, client_id: str, media_id: str) -> typing.Optional[Download]:
        data = self.base.get(media_id)
        download = Download(**data)
        download._file_path = Path(data["_file_path"])
        return download

    def update_download_progress(self, progress_obj: DownloadProgress):
        media_id = progress_obj.media_id
        status = progress_obj.status
        progress = progress_obj.progress
        self.base.update({"status": status, "progress": progress}, media_id)

    def get_download_if_exists(
        self, url: AnyHttpUrl, media_format: MediaFormatOptions
    ) -> typing.Optional[Download]:
        downloads_filtered = next(
            self.base.fetch({"video_url": url, "media_format": media_format})
        )
        return parse_obj_as(typing.List[Download], downloads_filtered)
