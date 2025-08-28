"""
Configuration exception types for the application.
"""

from fastapi import status

from app.core.exceptions.types.base import HTTPException


class ConfigError(HTTPException):
    """
    Exception for handling configuration validation errors.
    """

    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Configuration error: {message}",
            error="Invalid configuration",
        )
