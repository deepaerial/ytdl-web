import pathlib
import uvicorn


def serve():
    kwargs = {
        "host": "127.0.0.1",
        "port": 8000,
        "log_level": "debug",
        "reload": True,
        "ssl_keyfile": pathlib.Path("./certs/localhost+1-key.pem").as_posix(),
        "ssl_certfile": pathlib.Path("./certs/localhost+1.pem").as_posix(),
    }
    uvicorn.run("ytdl_api.asgi:app", **kwargs)


if __name__ == "__main__":
    serve()
