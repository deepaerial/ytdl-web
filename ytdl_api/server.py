import uvicorn


def serve():
    kwargs = {
        "host": "127.0.0.1",
        "port": 8000,
        "log_level": "debug",
        "reload": True,
    }
    uvicorn.run("ytdl.asgi:app", **kwargs)


if __name__ == "__main__":
    serve()
