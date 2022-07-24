FROM python:3.8-buster as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.4

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
# Install poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" && poetry config virtualenvs.create false
# Copy project files
COPY pyproject.toml poetry.lock /app/
# Project initialization: installing project's Python dependencies
# RUN poetry install --no-dev --no-interaction --no-ansi
# Copying API codebase
COPY ./ytdl_api ./ytdl_api
# Opening port
EXPOSE 80
########### Dev ###############
FROM base as dev
# Installing dev dependencies
RUN poetry install
# Running uvicorn server
CMD ["uvicorn", "ytdl_api.asgi:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug", "--reload"]

############ Test ###################
FROM dev as test
WORKDIR /app

RUN pip install debugpy

CMD ["pytest", "--cov-report", "html"]
############ Prod ###################
FROM base as prod
CMD ["uvicorn", "ytdl_api.asgi:app", "--host", "0.0.0.0", "--port", "80"]