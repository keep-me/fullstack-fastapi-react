"""
API routers.
"""

from fastapi import APIRouter

from app.api.endpoints import auth, users
from app.core.config import settings

api_router = APIRouter()

api_router.include_router(auth.router, tags=["Auth"], prefix=settings.API_V1_STR)
api_router.include_router(users.router, tags=["Users"], prefix=settings.API_V1_STR)
