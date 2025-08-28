"""
Other error handlers.
"""

from aiosmtplib.errors import SMTPException
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.core.exceptions.handlers.utils import log_exception
from app.core.exceptions.types.validation import ValidationError
from app.utils.response import create_response


def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle request validation errors.
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    message = "Validation error"
    error = str(exc)

    log_exception(
        request=request,
        exc=exc,
        status_code=status_code,
        message=message,
        error=error,
        level="warning",
    )

    return create_response(
        message=message,
        error=error,
        status_code=status_code,
        request=request,
    )


def smtp_exception_handler(request: Request, exc: SMTPException) -> JSONResponse:
    """
    Handle SMTP errors.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Email service error. Please, try again later."
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


def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Handle rate limit exceeded errors.
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Too many requests. Please, try again later."
    error = str(exc)

    log_exception(
        request=request,
        exc=exc,
        status_code=status_code,
        message=message,
        error=error,
        level="warning",
    )

    return create_response(
        message=message,
        error=error,
        status_code=status_code,
        request=request,
    )


def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle custom validation errors.
    """
    status_code = exc.status_code
    message = exc.message
    error = exc.error
    level = "warning"

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
