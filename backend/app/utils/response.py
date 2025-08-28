"""
Response utilities for the application.
"""

from typing import Any, TypeVar

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.models.schemas.response import ResponseBase

T = TypeVar("T")


def create_response(
    *,
    data: T | None = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    error: str | None = None,
    meta: dict[str, Any] | None = None,
    request: Request | None = None,
) -> JSONResponse:
    """
    Create a standardized JSON response.
    """
    is_success = 200 <= status_code < 300

    if meta is None:
        meta = {}

    if request and hasattr(request.state, "request_id"):
        meta["request_id"] = str(request.state.request_id)
    elif "request_id" not in meta:
        meta["request_id"] = None

    response = (
        ResponseBase[T].success_response(data=data, message=message, meta=meta)
        if is_success
        else ResponseBase[T].error_response(message=message, error=error, meta=meta)
    )

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True),
    )
