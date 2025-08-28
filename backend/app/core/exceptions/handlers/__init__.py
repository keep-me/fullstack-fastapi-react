"""
Error handlers for the application.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any, cast

from aiosmtplib.errors import SMTPException
from fastapi import FastAPI, Request, Response
from fastapi import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from jwt.exceptions import PyJWTError
from redis.exceptions import RedisError
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.handlers.auth import jwt_error_handler
from app.core.exceptions.handlers.database import (
    database_error_handler,
    redis_error_handler,
    sqlalchemy_error_handler,
)
from app.core.exceptions.handlers.http import (
    fastapi_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.core.exceptions.handlers.other import (
    rate_limit_handler,
    smtp_exception_handler,
    validation_error_handler,
    validation_exception_handler,
)
from app.core.exceptions.types import (
    DatabaseError,
    HTTPException,
    ValidationError,
)

log = logging.getLogger(__name__)

ExceptionHandler = Callable[[Request, Any], Awaitable[Response]]


def register_error_handlers(app: FastAPI) -> None:
    """
    Register all error handlers for FastAPI application.
    """
    app.add_exception_handler(
        FastAPIHTTPException,
        cast("ExceptionHandler", fastapi_exception_handler),
    )
    app.add_exception_handler(
        HTTPException,
        cast("ExceptionHandler", http_exception_handler),
    )

    app.add_exception_handler(PyJWTError, cast("ExceptionHandler", jwt_error_handler))

    app.add_exception_handler(
        SQLAlchemyError,
        cast("ExceptionHandler", sqlalchemy_error_handler),
    )
    app.add_exception_handler(RedisError, cast("ExceptionHandler", redis_error_handler))
    app.add_exception_handler(
        DatabaseError,
        cast("ExceptionHandler", database_error_handler),
    )

    app.add_exception_handler(
        ValidationError,
        cast("ExceptionHandler", validation_error_handler),
    )

    app.add_exception_handler(
        RequestValidationError,
        cast("ExceptionHandler", validation_exception_handler),
    )
    app.add_exception_handler(
        SMTPException,
        cast("ExceptionHandler", smtp_exception_handler),
    )
    app.add_exception_handler(
        RateLimitExceeded,
        cast("ExceptionHandler", rate_limit_handler),
    )

    app.add_exception_handler(
        Exception,
        cast("ExceptionHandler", unhandled_exception_handler),
    )
