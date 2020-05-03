from . import endpoints
from .config import settings

app = settings.init_app()
app.include_router(endpoints.router, prefix="/api")
