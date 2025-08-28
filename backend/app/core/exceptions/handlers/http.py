"""
HTTP error handlers.
"""

import logging

from fastapi import HTTPException as FastAPIHTTPException
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions.handlers.utils import log_exception
from app.core.exceptions.types import HTTPException
from app.utils.response import create_response

log = logging.getLogger("app")


def fastapi_exception_handler(
    request: Request,
    exc: FastAPIHTTPException,
) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions.
    """
    status_code = exc.status_code
    message = "Authentication required" if status_code == 401 else str(exc.detail)
    error = "Authentication failed" if status_code == 401 else None
    level = "warning" if status_code < 500 else "error"

    log_exception(
        request=request,
        exc=exc,
        status_code=status_code,
        message=message,
        error=error,
        level=level,
    )

    return create_response(
        message=message,
        error=error,
        status_code=status_code,
        request=request,
    )


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle custom HTTP exceptions.
    """
    status_code = exc.status_code
    message = exc.message if hasattr(exc, "message") else str(exc.detail)
    error = exc.error if hasattr(exc, "error") else None
    level = "warning" if exc.status_code < 500 else "error"

    log_exception(
        request=request,
        exc=exc,
        status_code=status_code,
        message=message,
        error=error,
        level=level,
    )

    return create_response(
        message=message,
        error=error,
        status_code=status_code,
        request=request,
    )


def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unhandled exceptions.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "An unknown error occurred. Please, try again later."
    error = str(exc)

    log_exception(
        request=request,
        exc=exc,
        status_code=status_code,
        message=message,
        error=error,
        level="error",
    )

    return create_response(
        message=message,
        error=error,
        status_code=status_code,
        request=request,
    )
