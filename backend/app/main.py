"""
Main application file.
"""

import logging.config
import os
import platform
from typing import Any, cast

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from slowapi.errors import RateLimitExceeded

from app.api.routers import api_router
from app.core.app import create_app
from app.core.config import settings
from app.core.events import lifespan
from app.core.exceptions import register_error_handlers
from app.core.exceptions.handlers import ExceptionHandler
from app.core.limiter import limiter, rate_limit_handler
from app.core.middleware import RequestIDMiddleware
from app.core.rabbit_mq import rabbit_router

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(f"app.{__name__}")
logger.info(f"Starting application in {settings.ENVIRONMENT} environment")

if os.getenv("TESTING") != "1":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=settings.PROJECT_VERSION,
        attach_stacktrace=True,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        send_default_pii=True,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        profile_session_sample_rate=1.0,
        profile_lifecycle="trace",
        shutdown_timeout=5,
        transport_queue_size=10000,
    )

app = create_app(lifespan=lifespan)


logger.debug("Registering middleware and routers")


if settings.ENVIRONMENT == "local":
    from app.core.profiler import PyInstrumentMiddleWare

    app.add_middleware(PyInstrumentMiddleWare)


if settings.ENVIRONMENT == "production" and limiter:
    from prometheus_fastapi_instrumentator import Instrumentator
    from slowapi.middleware import SlowAPIMiddleware

    Instrumentator().instrument(app).expose(app)

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(
        RateLimitExceeded,
        cast("ExceptionHandler", rate_limit_handler),
    )
    logger.info("Rate limiting middleware enabled")

app.include_router(api_router)
app.include_router(rabbit_router)
register_error_handlers(app)
logger.debug("Application setup complete")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}


app.add_middleware(RequestIDMiddleware)


if platform.system() != "Windows":
    import gunicorn.app.base

    class StandaloneApplication(gunicorn.app.base.BaseApplication):  # type: ignore
        """
        Standalone application for running the FastAPI app.
        """

        def __init__(self, app: Any, options: dict[str, Any] | None = None) -> None:
            """
            Initialize the standalone application.
            """
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self) -> None:
            """
            Load configuration from options.
            """
            config = {
                key: value
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            }
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self) -> Any:
            """
            Load the application.
            """
            return self.application


if __name__ == "__main__":
    if platform.system() == "Windows":
        import uvicorn

        logger.info(f"Starting server on {settings.SERVER_HOST}:{settings.SERVER_PORT}")
        uvicorn.run(
            "app.main:app",
            host=settings.SERVER_HOST,
            port=settings.SERVER_PORT,
            reload=True,
        )
    else:
        logger.info(f"Starting server on {settings.SERVER_HOST}:{settings.SERVER_PORT}")

        options = {
            "bind": f"{settings.SERVER_HOST}:{settings.SERVER_PORT}",
            "workers": settings.SERVER_WORKERS,
            "worker_class": "uvicorn.workers.UvicornWorker",
            "timeout": 90,
            "keepalive": 10,
            "worker_connections": 1000,
            "graceful_timeout": 60,
            "limit_request_line": 8190,
            "limit_request_fields": 100,
            "limit_request_field_size": 8190,
            "loglevel": f"{settings.LOG_LEVEL.lower()}",
            "preload_app": True,
            "reuse_port": True,
            "capture_output": True,
            "errorlog": "-",
            "accesslog": "-",
        }

        StandaloneApplication(app, options).run()
