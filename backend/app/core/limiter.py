"""
Rate limiting functionality.
"""

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_remote_ip(request: Request) -> str:
    """
    Get client IP address.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    return get_remote_address(request)


limiter = Limiter(
    key_func=_get_remote_ip,
    storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    enabled=settings.ENVIRONMENT == "production",
)

limit = limiter.limit


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Rate limit exceeded handler.
    """
    client_ip = _get_remote_ip(request)
    logger.warning(
        f"Rate limit exceeded for client '{client_ip}' on path '{request.url.path}'",
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
        },
        headers={"Retry-After": "60"},
    )
