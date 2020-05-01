import socketio

from fastapi import FastAPI

from . import __version__
from . import endpoints
from .config import settings

app = FastAPI(
    debug=True,
    title="YTDL API",
    description="API for YTDL backend server.",
    version=__version__,
)

settings.init_app(app)
app.include_router(endpoints.router, prefix="/api")

