"""
Unit tests for request middleware functionality.
"""

import logging
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import Header, Request, status
from fastapi.responses import Response

from app.core.middleware import RequestIDMiddleware


@pytest.mark.asyncio
async def test_request_id_middleware_happy_path(caplog: Any) -> None:
    """
    Tests that the middleware adds a request_id and logs request/response details.
    """
    logging.getLogger("app.middleware")
    with caplog.at_level(logging.INFO, logger="app.middleware"):
        middleware = RequestIDMiddleware(app=MagicMock())
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/test"
        request.headers = {"user-agent": Header("pytest")}
        request.client.host = "127.0.0.1"

        async def call_next(req: Request) -> Response:
            assert hasattr(req.state, "request_id")
            assert isinstance(req.state.request_id, str)
            return Response(status_code=status.HTTP_200_OK, content=b"OK")

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == status.HTTP_200_OK
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] == request.state.request_id

        assert len(caplog.records) == 2
        assert "Incoming request" in caplog.records[0].message
        assert caplog.records[0].request_id == request.state.request_id
        assert "Request completed" in caplog.records[1].message
        assert caplog.records[1].request_id == request.state.request_id


@pytest.mark.asyncio
async def test_request_id_middleware_exception_handling(caplog: Any) -> None:
    """
    Tests that the middleware correctly logs errors from downstream handlers.
    """
    with caplog.at_level(logging.ERROR, logger="app.middleware"):
        middleware = RequestIDMiddleware(app=MagicMock())
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url.path = "/error"
        request.headers = {}
        request.client.host = "testclient"

        test_exception = ValueError("Something went wrong")

        async def call_next(req: Request) -> Response:
            raise test_exception

        with pytest.raises(ValueError, match="Something went wrong"):
            await middleware.dispatch(request, call_next)

        assert len(caplog.records) == 1
        assert "Request failed" in caplog.records[0].message
        assert caplog.records[0].error == str(test_exception)
        assert caplog.records[0].error_type == "ValueError"
        assert hasattr(request.state, "request_id")
        assert caplog.records[0].request_id == request.state.request_id
