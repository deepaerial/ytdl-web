from pathlib import Path
from typing import Any, Dict, Optional
from enum import Enum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseSettings, root_validator
from starlette.middleware import Middleware
from youtube_dl.version import __version__ as youtube_dl_version

from . import __version__

env_path = Path(__file__).parent / "config" / ".env"


class DbTypes(str, Enum):
    MEMORY = "memory"
    DETA = "deta"


class Settings(BaseSettings):
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
    version: str = __version__
    youtube_dl_version = youtube_dl_version
    disable_docs: bool = False

    # Path to directory where downloaded medias will be stored
    media_path: Path
    # Type of database to use
    db_type: DbTypes
    # Deta project key
    deta_key: Optional[str]
    # Deta base name
    deta_base: Optional[str]

    @root_validator
    def validate_deta_db(cls, values):
        db_type = values.get("db_type")
        if db_type == DbTypes.DETA:
            deta_key = values.get("deta_key")
            if not deta_key:
                raise ValueError("Deta key is required when using Deta Base service")
        return values

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
                    allow_origins=[
                        "http://localhost",
                        "http://localhost:8080",
                        "http://127.0.0.1",
                        "http://127.0.0.1:8080",
                    ],
                    allow_credentials=True,
                    allow_methods=["*"],
                    allow_headers=["*"],
                ),
            ],
        }
        if __pydantic_self__.disable_docs:
            kwargs.update({"docs_url": None, "openapi_url": None, "redoc_url": None})
        app = FastAPI(**kwargs)
        app.config = __pydantic_self__
        return app

    class Config:
        env_file = env_path
        allow_mutation = True
        case_sensitive = False


settings = Settings()
