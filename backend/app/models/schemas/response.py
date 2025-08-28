from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    """
    Base response model for all API responses
    """

    success: bool
    message: str
    data: T | None = None
    error: str | None = None
    meta: dict[str, Any] | None = None

    @classmethod
    def success_response(
        cls,
        data: T | None = None,
        message: str = "Success",
        meta: dict[str, Any] | None = None,
    ) -> "ResponseBase[T]":
        """
        Create a success response
        """
        return cls(success=True, message=message, data=data, meta=meta)

    @classmethod
    def error_response(
        cls,
        message: str,
        error: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> "ResponseBase[T]":
        """
        Create an error response
        """
        return cls(success=False, message=message, error=error, meta=meta)
