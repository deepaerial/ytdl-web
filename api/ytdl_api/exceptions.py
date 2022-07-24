import re
import socket
from http.client import RemoteDisconnected

from starlette.responses import JSONResponse

_ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")


def make_internal_error(error_code: str = "internal-server-error") -> JSONResponse:
    return JSONResponse(
        {
            "detail": "Remote server encountered problem, please try again...",
            "code": error_code,
        },
        status_code=500,
    )


async def on_remote_disconnected(request, exc: RemoteDisconnected):
    return make_internal_error("external-service-network-error")


async def on_socket_timeout(request, exc: socket.timeout):
    return make_internal_error("external-service-timeout-error")


async def on_runtimeerror(request, exc: RuntimeError):
    return make_internal_error()


ERROR_HANDLERS = (
    (RemoteDisconnected, on_remote_disconnected),
    (socket.timeout, on_socket_timeout),
    (RuntimeError, on_runtimeerror),
)
