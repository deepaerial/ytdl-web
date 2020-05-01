from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseSettings

env_path = Path(__file__).parent / "config" / ".env"


class Settings(BaseSettings):
    """
    Application settings config
    """

    media_path: Path

    def init_app(__pydantic_self__, app: FastAPI):
        app.config = __pydantic_self__

    class Config:
        env_file = env_path
        allow_mutation = True
        case_sensitive = False


settings = Settings()
