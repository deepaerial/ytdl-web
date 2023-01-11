import abc
import json
from pathlib import Path
from typing import Any, Dict, List, Union

import pkg_resources
from confz import ConfZ, ConfZEnvSource
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import validator
from starlette.middleware import Middleware

from .constants import DownloaderType
from .datasource import IDataSource, DetaDB
from .storage import IStorage, LocalFileStorage

MEDIA_PATH = (Path(__file__).parent / ".." / ".." / "media").resolve()


class BaseDataSourceConfig(ConfZ, abc.ABC):
    """
    Base abstract class for datasource config class.
    """

    @abc.abstractmethod
    def get_datasource(self) -> IDataSource:  # pragma: no cover
        raise NotImplementedError

    # In order to avoid TypeError: unhashable type: 'Settings' when overidding
    # dependencies.get_settings in tests.py __hash__ should be implemented
    def __hash__(self):  # make hashable BaseModel subclass
        attrs = tuple(
            attr if not isinstance(attr, list) else ",".join(attr)
            for attr in self.__dict__.values()
        )
        return hash((type(self),) + attrs)


class DetaBaseDataSourceConfig(BaseDataSourceConfig):
    """
    Deta Base DB datasource config.
    """

    deta_key: str
    deta_base: str

    def get_datasource(self) -> IDataSource:
        return DetaDB(self.deta_key, self.deta_base)


class BaseStorageConfig(ConfZ, abc.ABC):
    """
    Base abstract class for storage config class.
    """

    @abc.abstractmethod
    def get_storage(self) -> IStorage:  # pragma: no cover
        raise NotImplementedError


class LocalStorageConfig(BaseStorageConfig):
    """
    Local filesystem storage config.
    """

    path: Path = MEDIA_PATH

    @validator("path")
    def validate_path(cls, value):
        media_path = Path(value)
        if not media_path.exists():  # pragma: no cover
            print(f'Media path "{value}" does not exist...Creating...')
            media_path.mkdir(parents=True)
        return value

    def get_storage(self) -> IStorage:
        return LocalFileStorage(self.path)


class Settings(ConfZ):
    """
    Application settings config
    """

    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "YTDL API"
    description: str = "API for YTDL backend server."
    version: str = pkg_resources.get_distribution("ytdl-api").version
    disable_docs: bool = False
    allow_origins: List[str]
    cookie_samesite: str = "None"
    cookie_secure: bool = True
    cookie_httponly: bool = True

    downloader: DownloaderType
    media_path: Path = MEDIA_PATH
    datasource: DetaBaseDataSourceConfig

    CONFIG_SOURCES = ConfZEnvSource(
        allow_all=True, deny=["title", "description", "version"], nested_separator="__"
    )

    @validator("allow_origins", pre=True)
    def validate_allow_origins(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value

    def init_app(__pydantic_self__) -> FastAPI:
        """
        Generate FastAPI instance.
        """
        kwargs: Dict[str, Any] = {
            "debug": __pydantic_self__.debug,
            "docs_url": __pydantic_self__.docs_url,
            "openapi_prefix": __pydantic_self__.openapi_prefix,
            "openapi_url": __pydantic_self__.openapi_url,
            "redoc_url": __pydantic_self__.redoc_url,
            "title": __pydantic_self__.title,
            "description": __pydantic_self__.description,
            "version": __pydantic_self__.version,
            "middleware": [
                Middleware(
                    CORSMiddleware,
                    allow_origins=__pydantic_self__.allow_origins,
                    allow_credentials=True,
                    allow_methods=["*"],
                    allow_headers=["*"],
                    expose_headers=["Content-Disposition"],
                ),
            ],
        }
        if __pydantic_self__.disable_docs:
            kwargs.update({"docs_url": None, "openapi_url": None, "redoc_url": None})
        app = FastAPI(**kwargs)
        __pydantic_self__.__setup_endpoints(app)
        __pydantic_self__.__setup_exception_handlers(app)
        return app

    def __setup_endpoints(__pydantic_self__, app: FastAPI):
        from .endpoints import router

        app.include_router(router, prefix="/api")

    def __setup_exception_handlers(__pydantic_self__, app: FastAPI):
        from .exceptions import ERROR_HANDLERS

        for error, handler in ERROR_HANDLERS:
            app.add_exception_handler(error, handler)

    # In order to avoid TypeError: unhashable type: 'Settings' when overidding
    # dependencies.get_settings in tests.py __hash__ should be implemented
    def __hash__(self):  # make hashable BaseModel subclass
        attrs = tuple(
            attr if not isinstance(attr, list) else ",".join(attr)
            for attr in self.__dict__.values()
        )
        return hash((type(self),) + attrs)

    class Config:
        allow_mutation = True
        case_sensitive = False
