import humps
from pydantic import BaseModel


class BaseModel_(BaseModel):
    """Base class for all schemas."""

    class Config:
        alias_generator = humps.camelize
        allow_population_by_field_name = True
