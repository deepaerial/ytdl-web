import itertools
import typing
from abc import ABC, abstractmethod
from collections import defaultdict

from deta import Deta
from pydantic import AnyHttpUrl, parse_obj_as

from .constants import DownloadStatus, MediaFormat
from .schemas.models import Download, DownloadProgress


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
    def put_download(self, download: Download):  # pragma: no cover
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
    def update_download(self, download: Download):  # pragma: no cover
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

    @abstractmethod
    def delete_download(self, download: Download):  # pragma: no cover
        """
        Abstract method for deleting download in media database.
        """

    def clear_downloads(self):
        raise NotImplementedError()


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
        downloads = self.base.fetch(
            {"client_id": client_id, "status?ne": DownloadStatus.DELETED}
        ).items
        return parse_obj_as(typing.List[Download], downloads)

    def put_download(self, download: Download):
        data = download.dict()
        key = data["media_id"]
        if download.file_path is not None:
            data["file_path"] = download.file_path.resolve().as_posix()
        self.base.put(data, key)

    def get_download(self, client_id: str, media_id: str) -> typing.Optional[Download]:
        data = next(
            iter(self.base.fetch({"client_id": client_id, "media_id": media_id}).items),
            None,
        )
        if data is None:
            return data
        download = Download(**data)
        return download

    def update_download(self, download: Download):
        data = download.dict()
        # quick fix for error TypeError: Object of type PosixPath is not JSON serializable
        if download.file_path is not None:
            data["file_path"] = download.file_path.resolve().as_posix()
        self.base.update(data, download.media_id)

    def update_download_progress(self, progress_obj: DownloadProgress):
        media_id = progress_obj.media_id
        status = progress_obj.status
        progress = progress_obj.progress
        self.base.update({"status": status, "progress": progress}, media_id)

    def get_download_if_exists(
        self, url: AnyHttpUrl, media_format: MediaFormat
    ) -> typing.Optional[Download]:
        filtered_download = self.base.fetch(
            {"video_url": url, "media_format": media_format}
        ).items
        if isinstance(filtered_download, list):
            if not filtered_download:
                return None
            filtered_download = filtered_download[0]
        download: Download = parse_obj_as(Download, filtered_download)
        return download

    def delete_download(self, download: Download):
        self.base.delete(download.media_id)

    def clear_downloads(self):
        all_downloads = self.base.fetch().items
        for download in all_downloads:
            self.base.delete(download["key"])
        self.base.client.close()
