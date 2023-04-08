FROM python:3.10-bullseye as base

EXPOSE 80

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.0

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y ffmpeg

# Install poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" && poetry config virtualenvs.in-project true

FROM base as project-base
WORKDIR /app
# Copy project files
COPY pyproject.toml poetry.lock /app/
# Project initialization: installing project's Python dependencies
RUN poetry install --no-root --without dev
COPY ./ytdl_api /app/ytdl_api
# Opening port
########### Dev ###############
FROM project-base as dev
COPY --from=project-base /app/.venv /app/.venv
# Installing dev dependencies
RUN poetry install
# Running uvicorn server
CMD ["poetry", "run", "uvicorn", "ytdl_api.asgi:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug", "--reload"]

############ Test ###################
FROM dev as test
COPY --from=project-base /app/.venv /app/.venv
RUN poetry install
CMD ["pytest", "--cov-report", "html"]
############ Prod ###################
FROM project-base as prod
RUN poetry install --without dev
CMD ["poetry", "run", "uvicorn", "ytdl_api.asgi:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug"]