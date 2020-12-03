from abc import ABC, abstractmethod
from collections import defaultdict
import typing


from .schemas import Download


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
        instance = next(iter([
            d for d in self.storage[client_id] if d.media_id == media_id
        ]), None)
        return instance
