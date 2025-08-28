"""
Utility functions for error handlers.
"""

import logging
from typing import Any, Literal

import sentry_sdk
from fastapi import Request

log = logging.getLogger("app")

LogLevel = Literal["fatal", "critical", "error", "warning", "info", "debug"]


def log_exception(
    request: Request,
    exc: Exception,
    status_code: int,
    message: str,
    error: str | None = None,
    level: str = "warning",
) -> None:
    """
    Log exception and send to Sentry.
    """
    extra = {
        "status_code": status_code,
        "path": str(request.url.path),
        "method": request.method,
        "client_ip": request.client.host if request.client else None,
        "error_message": message,
    }

    if hasattr(request.state, "request_id"):
        extra["request_id"] = str(request.state.request_id)

    if error:
        extra["error_detail"] = error

    if level == "warning":
        log.warning(message, extra=extra)
    else:
        log.error(message, exc_info=exc, extra=extra)

    sentry_sdk.set_context(
        "request",
        {
            "url": str(request.url),
            "method": request.method,
            "path_params": request.path_params,
            "headers": dict(request.headers),
            "client": request.client.host if request.client else None,
        },
    )

    sentry_level: LogLevel = "warning"
    if level == "error":
        sentry_level = "error"

    sentry_sdk.set_level(sentry_level)
    sentry_sdk.capture_exception(exc)


def get_request_meta(request: Request) -> dict[str, Any]:
    """
    Get request metadata for error response.
    """
    return {
        "request_id": str(request.state.request_id)
        if hasattr(request.state, "request_id")
        else None,
        "path": str(request.url.path),
    }
