"""
JWT authentication error handlers.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidTokenError,
    PyJWTError,
)

from app.core.exceptions.handlers.utils import log_exception
from app.utils.response import create_response


def jwt_error_handler(request: Request, exc: PyJWTError) -> JSONResponse:
    """
    Handle JWT authentication errors.
    """

    message = "Authentication error. Please, try again."

    if isinstance(exc, ExpiredSignatureError):
        message = "Token has expired. Please, log in again."
    elif isinstance(exc, (InvalidTokenError, DecodeError)):
        message = "Invalid token. Please, log in again."

    log_exception(
        request=request,
        exc=exc,
        status_code=status.HTTP_401_UNAUTHORIZED,
        message=message,
        error=str(exc),
        level="warning",
    )

    return create_response(
        message=message,
        error=str(exc),
        status_code=status.HTTP_401_UNAUTHORIZED,
        request=request,
    )
