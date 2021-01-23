FROM python:3.7

WORKDIR /app
# Install poetry
RUN pip install poetry
# Install ffmpeg
RUN apk add  --no-cache ffmpeg gst-libav
# Copy project files
COPY pyproject.toml poetry.lock ./
# Install dependencies
RUN poetry install --no-root --no-dev --no-ansi
# Copying API codebase
COPY ./ytdl_api ./
# Opening port
EXPOSE 80
# Running uvicorn server
СMD ['uvicorn', 'ytdl_api.asgi:app', '--host', '0.0.0.0', '--port', '80', '--log-level', 'info']