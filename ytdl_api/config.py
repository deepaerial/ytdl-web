from typing import Dict, Any
from pathlib import Path
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette_authlib.middleware import AuthlibMiddleware as SessionMiddleware
from pydantic import BaseSettings

from . import __version__

env_path = Path(__file__).parent / "config" / ".env"


class Settings(BaseSettings):
    """
    Application settings config
    """

    secret_key: str
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "YTDL API"
    description: str = "API for YTDL backend server."
    version: str = __version__
    disable_docs: bool = False

    media_path: Path

    def init_app(__pydantic_self__) -> FastAPI:
        '''
        Generate FastAPI instance.
        '''
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
                Middleware(SessionMiddleware, secret_key=__pydantic_self__.secret_key)
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
