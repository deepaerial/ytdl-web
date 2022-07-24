#!/bin/bash
poetry run uvicorn ytdl_api.asgi:app --host 127.0.0.1 --port 8080  --env-file .env