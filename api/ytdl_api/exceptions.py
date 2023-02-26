import socket
from http.client import RemoteDisconnected
from logging import Logger

from fastapi.requests import Request
from starlette.responses import JSONResponse


def make_internal_error(error_code: str = "internal-server-error") -> JSONResponse:
    return JSONResponse(
        {
            "detail": "Remote server encountered problem, please try again...",
            "code": error_code,
        },
        status_code=500,
    )


async def on_remote_disconnected(
    logger: Logger, request: Request, exc: RemoteDisconnected
):
    logger.exception(exc)
    return make_internal_error("external-service-network-error")


async def on_socket_timeout(logger: Logger, request: Request, exc: socket.timeout):
    logger.exception(exc)
    return make_internal_error("external-service-timeout-error")


async def on_runtimeerror(logger: Logger, request: Request, exc: RuntimeError):
    logger.exception(exc)
    return make_internal_error()


ERROR_HANDLERS = (
    (RemoteDisconnected, on_remote_disconnected),
    (socket.timeout, on_socket_timeout),
    (RuntimeError, on_runtimeerror),
)
