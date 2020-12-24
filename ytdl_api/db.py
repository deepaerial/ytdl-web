from abc import ABC, abstractmethod
from collections import defaultdict
import typing
import itertools

from pydantic import AnyHttpUrl

from .schemas import Download, MediaFormatOptions


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
    def update_download_progress(self, client_id: str, media_id: str, progress: int):
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
    SQLite implementation for DAOInterface.
    """

    storage: typing.DefaultDict[str, typing.List[Download]] = defaultdict(list)

    def fetch_downloads(self, client_id: str) -> typing.List[Download]:
        return self.storage[client_id]

    def put_download(self, client_id: str, download: Download):
        self.storage[client_id].append(download)

    def get_download(self, client_id: str, media_id: str) -> typing.Optional[Download]:
        return next(
            filter(lambda d: d.media_id == media_id, self.storage[client_id]), None,
        )

    def update_download_progress(self, client_id: str, media_id: str, progress: int):
        download = self.get_download(client_id, media_id)
        download.progress = progress

    def get_download_if_exists(
        self, url: AnyHttpUrl, media_format: MediaFormatOptions
    ) -> typing.Optional[Download]:
        downloads = list(itertools.chain.from_iterable(self.storage.values()))
        return next(
            filter(
                lambda d: d.video_url == url and d.media_format == media_format,
                downloads
            ),
            None,
        )
