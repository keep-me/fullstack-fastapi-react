"""
Local settings for the application.
"""

import secrets
from typing import ClassVar, Literal

from pydantic_settings import SettingsConfigDict

from app.core.config.base import BASE_DIR

from .base import BaseAppSettings
from .components import (
    AuthSettings,
    DatabaseSettings,
    EmailSettings,
    LoggingSettings,
    RabbitMQSettings,
    RedisSettings,
    ServerSettings,
    UserSettings,
)


class LocalSettings(
    BaseAppSettings,
    ServerSettings,
    DatabaseSettings,
    AuthSettings,
    UserSettings,
    LoggingSettings,
    RedisSettings,
    RabbitMQSettings,
    EmailSettings,
):
    """
    Settings for local development environment.
    """

    ENVIRONMENT: Literal["local", "production"] = "local"

    PROJECT_NAME: str = "FastAPI Full Stack Local"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    LOG_LEVEL: str = "INFO"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env.local"),
        env_ignore_empty=True,
        extra="ignore",
    )
