"""
Middleware for the application.
"""

import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("app.middleware")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding a unique request_id to each request.

        Sets request_id in request.state for use in logs and responses.
        Logs each request with detailed information.

    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """
        Processes the request and adds request_id.

                Args:
                    request: FastAPI request object
                    call_next: Next middleware or endpoint

                Returns:
                    Response: Response with request_id set in headers


        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        self._log_request(request, request_id)

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            self._log_response(request, response, request_id, process_time)
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "process_time": f"{process_time:.3f}s",
                    "error": str(exc),
                    "error_type": exc.__class__.__name__,
                },
            )
            raise

    def _log_request(self, request: Request, request_id: str) -> None:
        """
        Logs the incoming request.

                Args:
                    request: FastAPI request object
                    request_id: Unique request identifier


        """
        headers = dict(request.headers)
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        filtered_headers = {
            k: "***" if k.lower() in sensitive_headers else v
            for k, v in headers.items()
        }

        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": filtered_headers,
                "client_ip": request.client.host if request.client else None,
                "user_agent": headers.get("user-agent", "Unknown"),
            },
        )

    def _log_response(
        self,
        request: Request,
        response: Response,
        request_id: str,
        process_time: float,
    ) -> None:
        """
        Logs the response to the request.

                Args:
                    request: FastAPI request object
                    response: FastAPI response object
                    request_id: Unique request identifier
                    process_time: Request execution time in seconds


        """
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
                "response_size": len(response.body)
                if hasattr(response, "body") and response.body
                else 0,
            },
        )
