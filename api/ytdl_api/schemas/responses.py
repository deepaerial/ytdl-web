from typing import List

from pydantic import (
    BaseModel,
    Field,
)
from ..constants import ProgressStatusEnum
from .models import Download


class ErrorResponse(BaseModel):
    detail: str = Field(
        ..., description="Message detail", example="Internal server error"
    )
    code: str = Field(description="Custom error identifying code")


class DownloadsResponse(BaseModel):
    downloads: List[Download] = Field(
        ..., description="List of pending and finished downloads",
    )


class VersionResponse(BaseModel):
    api_version: str


class DeleteResponse(BaseModel):
    media_id: str = Field(..., description="Id of downloaded media")
    status: ProgressStatusEnum = Field(
        ..., description="Download status", example=ProgressStatusEnum.DELETED
    )
