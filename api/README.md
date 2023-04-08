 # YTDL-API
REST-based API for downloading video or extracting audio from YouTube videos.  Also [ffmpeg](https://ffmpeg.org/) is required in order to process video and audio files.
<br><br>

![OpenAPI documentation for YTDL API](./docs/openapi.png)

## Requirements
App requires Python 3.8 and [poetry](https://python-poetry.org/) installed. Also project relies on [Deta](https://www.deta.sh/) for storing data about downloads. So you should have account there in order to run this project.

## Installation
Run `poetry` command below to install project dependencies (including ones needed for development).
```shell
$ poetry install
```
## Launch API locally
Before starting the application server you should create `.env` file which will contain all necessary settings. Example configuraion for Docker container:
```shell
DEBUG=True
ALLOW_ORIGINS="http://localhost,http://localhost:8080,http://localhost:8081,http://127.0.0.1,http://127.0.0.1:8080,http://127.0.0.1:8081"
DATASOURCE__DETA_KEY=<your Deta key should inserted here>
DATASOURCE__DETA_BASE=<your deta base name should be inserted here>
MEDIA_PATH="/app/media"
```
After you're done with configuration simply execute script below:
```shell
$ ./scripts/run_devserver.sh 
```
This will launch `uvicorn` server with app on http://localhost:8080. You will also be able to check OpenAPI (Swagger) documentation on http://localhost:8080/docs.

## Running app using docker-compose
```shell
$ docker-compose up -d ytdl_api
```

## Deploy on Fly.io
1. Set up machine for app container
```shell
$ fly launch --no-deploy
```    

2. Set environmental variables
```shell
$ fly secrets import
# your secrets are passed below
DEBUG=True
ALLOW_ORIGINS="http://localhost,http://localhost:8080,http://localhost:8081,http://127.0.0.1,http://127.0.0.1:8080,http://127.0.0.1:8081"
DATASOURCE__DETA_KEY=<your Deta key should inserted here>
DATASOURCE__DETA_BASE=<your deta base name should be inserted here>
EOL
```

3. Deploy app
```shell
$ fly deploy
```