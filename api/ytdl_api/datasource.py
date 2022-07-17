from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
import typing
import itertools

from deta import Deta
from pydantic import AnyHttpUrl, parse_obj_as

from .schemas.models import Download, DownloadProgress
from .constants import MediaFormat, ProgressStatusEnum


class IDataSource(ABC):
    """
    Abstract interface that provides abstract methods for accessing and manipulating data
    from database.
    """

    @abstractmethod
    def fetch_downloads(
        self, client_id: str
    ) -> typing.List[Download]:  # pragma: no cover
        """
        Abstract method that returns list of clients downloads from data source.
        """
        raise NotImplementedError

    @abstractmethod
    def put_download(self, client_id: str, download: Download):  # pragma: no cover
        """
        Abstract method for inserting download instance to data source.
        """
        raise NotImplementedError

    @abstractmethod
    def get_download(
        self, client_id: str, media_id: str
    ) -> typing.Optional[Download]:  # pragma: no cover
        """
        Abstract method for fetching download instance from data source
        """
        raise NotImplementedError

    @abstractmethod
    def update_download(self, client_id: str, download: Download):  # pragma: no cover
        """
        Abstract method for updating download instance from data source
        """
        raise NotImplementedError

    @abstractmethod
    def update_download_progress(
        self, progress_obj: DownloadProgress
    ):  # pragma: no cover
        """
        Abstract method that updates progress for media item of specific user/client.
        """
        raise NotImplementedError

    @abstractmethod
    def get_download_if_exists(
        self, url: AnyHttpUrl, media_format: MediaFormat
    ) -> typing.Optional[Download]:  # pragma: no cover
        """
        Abstract method that returns True if media with given url and media format exists
        in downloaded media database.
        """
        raise NotImplementedError


class InMemoryDB(IDataSource):
    """
    In-memory database implementation for DAOInterface.
    """

    storage: typing.DefaultDict[str, typing.List[Download]] = defaultdict(list)

    def fetch_downloads(self, client_id: str) -> typing.List[Download]:
        return (
            list(
                filter(
                    lambda d: d.status != ProgressStatusEnum.DELETED,
                    self.storage[client_id],
                )
            )
            or []
        )

    def put_download(self, client_id: str, download: Download):
        self.storage[client_id].append(download)

    def get_download(self, client_id: str, media_id: str) -> typing.Optional[Download]:
        return next(
            filter(lambda d: d.media_id == media_id, self.storage[client_id]), None,
        )

    def update_download(self, client_id: str, download: Download):
        donwloads = self.storage[client_id]
        index = next(
            (idx for idx, d in enumerate(donwloads) if d.media_id == download.media_id),
            None,
        )
        if index is None:
            self.storage[client_id].append(download)
        else:
            self.storage[client_id][index] = download

    def update_download_progress(self, progress_obj: DownloadProgress):
        download = self.get_download(progress_obj.client_id, progress_obj.media_id)
        download.progress = progress_obj.progress
        download.status = progress_obj.status

    def get_download_if_exists(
        self, url: AnyHttpUrl, media_format: MediaFormat
    ) -> typing.Optional[Download]:
        downloads = list(itertools.chain.from_iterable(self.storage.values()))
        return next(
            filter(
                lambda d: d.video_url == url and d.media_format == media_format,
                downloads,
            ),
            None,
        )


class DetaDB(IDataSource):
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
        downloads = next(
            self.base.fetch(
                {"client_id": client_id, "status?ne": ProgressStatusEnum.DELETED}
            )
        )
        return parse_obj_as(typing.List[Download], downloads)

    def put_download(self, client_id: str, download: Download):
        data = download.dict()
        data["client_id"] = client_id
        data["_file_path"] = download.file_path
        key = data["media_id"]
        self.base.put(data, key)

    def get_download(self, client_id: str, media_id: str) -> typing.Optional[Download]:
        data = next(
            iter(
                next(
                    self.base.fetch({"client_id": client_id, "media_id": media_id}), []
                )
            ),
            None,
        )
        if data is None:
            return data
        file_path = data.pop("_file_path")
        download = Download(**data)
        download._file_path = Path(file_path)
        return download

    def update_download(self, client_id: str, download: Download):
        data = download.dict()
        data["_file_path"] = download.file_path
        key = data.pop("media_id")
        self.base.update(data, key)

    def update_download_progress(self, progress_obj: DownloadProgress):
        media_id = progress_obj.media_id
        status = progress_obj.status
        progress = progress_obj.progress
        self.base.update({"status": status, "progress": progress}, media_id)

    def get_download_if_exists(
        self, url: AnyHttpUrl, media_format: MediaFormat
    ) -> typing.Optional[Download]:
        filtered_download = next(
            self.base.fetch({"video_url": url, "media_format": media_format})
        )
        if isinstance(filtered_download, list):
            if not filtered_download:
                return None
            filtered_download = filtered_download[0]
        download: Download = parse_obj_as(Download, filtered_download)
        download._file_path = Path(filtered_download["_file_path"])
        return download
