"""
FastAPI application creation.
"""

from collections.abc import Callable
from typing import Any, AsyncContextManager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

tags_metadata = [
    {
        "name": "Users",
        "description": "Operations with users",
    },
    {
        "name": "Auth",
        "description": "Authorization",
    },
]


def create_app(
    *,
    lifespan: Callable[[FastAPI], AsyncContextManager[Any]] | None = None,
) -> FastAPI:
    """
    Create FastAPI Application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        openapi_tags=tags_metadata,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    if settings.all_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Verification"],
        )

    return app
