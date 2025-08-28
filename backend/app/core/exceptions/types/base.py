"""
Base exception types for the application.
"""

from fastapi import HTTPException as FastAPIHTTPException


class HTTPException(FastAPIHTTPException):
    """
    Base HTTP exception class with additional fields for detailed error reporting.
    """

    def __init__(
        self,
        status_code: int,
        message: str = "An unexpected error occurred",
        error: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.error = error
        super().__init__(status_code=status_code, detail=error or message)

    def __str__(self) -> str:
        return f"{self.status_code}: {self.message}"
