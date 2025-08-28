"""
Database error handlers.
"""

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy.exc import MultipleResultsFound, SQLAlchemyError

from app.core.exceptions.handlers.utils import log_exception
from app.core.exceptions.types.database import DatabaseError
from app.utils.response import create_response

logger = logging.getLogger("app.exceptions.database")


def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle SQLAlchemy database errors.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Database error. Please, try again later."
    error = str(exc)
    level = "error"

    if isinstance(exc, MultipleResultsFound):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = "Data error. Please, try again later."
        error = "Multiple users found with these credentials"

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


def redis_error_handler(request: Request, exc: RedisError) -> JSONResponse:
    """
    Handle Redis database errors.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Redis error. Please, try again later."
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


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """
    Handle database-related errors.
    """
    logger.error(f"Database error: {exc.error} - {exc.message}")

    log_exception(
        request=request,
        exc=exc,
        status_code=exc.status_code,
        message=exc.message,
        error=exc.error,
        level="error",
    )

    return create_response(
        message=exc.message,
        error=exc.error,
        status_code=exc.status_code,
        request=request,
    )
