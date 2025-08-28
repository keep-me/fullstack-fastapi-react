"""
Unit tests for rate limiting functionality.
"""

import importlib
import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from app.core import limiter
from app.core.limiter import _get_remote_ip, rate_limit_handler
from tests.parametrized_test_data import limiter_param_data


# fmt: off
@pytest.mark.parametrize(
    "headers, expected_ip",
    limiter_param_data,
    ids=["multiple_forwarded_ips", "single_forwarded_ip", "real_ip", "no_client", "bad_ip", "stripped_ip"],
)
# fmt: on
def test_get_remote_ip(headers: dict[str, str], expected_ip: str) -> None:
    """
Tests extracting IP address from headers.
"""
    scope = {
        "type": "http",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "client": ("127.0.0.1", 8000),
    }
    request = Request(scope)

    result = _get_remote_ip(request)
    assert result == expected_ip


def test_limiter_initialization(monkeypatch: Any) -> None:
    """
Tests that limiter is always enabled and configured to use Redis.
"""
    monkeypatch.setattr("app.core.limiter.settings.REDIS_HOST", "localhost")
    monkeypatch.setattr("app.core.limiter.settings.REDIS_PORT", 6379)
    monkeypatch.setattr("app.core.limiter.settings.REDIS_DB", 0)

    importlib.reload(limiter)

    assert isinstance(limiter.limiter, Limiter)
    assert limiter.limiter.enabled is not None
    assert limiter.limiter.limiter.storage is not None


@pytest.mark.asyncio
async def test_rate_limit_handler() -> None:
    """
Tests the rate limit exceeded handler.
"""
    scope = {
        "type": "http",
        "headers": [],
        "client": ("127.0.0.1", 8000),
        "path": "/test",
    }
    request = Request(scope)

    exc = MagicMock(spec=RateLimitExceeded)
    exc.detail = "Rate limit exceeded"

    with patch("app.core.limiter.logger") as mock_logger:
        response = await rate_limit_handler(request, exc)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"

    mock_logger.warning.assert_called_once_with(
        "Rate limit exceeded for client '127.0.0.1' on path '/test'",
    )

    content = bytes(response.body).decode("utf-8")

    response_data = json.loads(content)

    assert response_data["error"] == "rate_limit_exceeded"
    assert response_data["message"] == "Too many requests. Please try again later."
