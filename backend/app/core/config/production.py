"""
Production settings for the application.
"""

from typing import ClassVar, Literal

from pydantic_settings import SettingsConfigDict

from .base import BaseAppSettings
from .components import (
    AuthSettings,
    DatabaseSettings,
    EmailSettings,
    LoggingSettings,
    RabbitMQSettings,
    RedisSettings,
    SecuritySettings,
    ServerSettings,
    UserSettings,
)


class ProductionSettings(
    BaseAppSettings,
    ServerSettings,
    DatabaseSettings,
    AuthSettings,
    UserSettings,
    LoggingSettings,
    RedisSettings,
    SecuritySettings,
    RabbitMQSettings,
    EmailSettings,
):
    """
    Settings for production environment with strict security requirements.
    """

    ENVIRONMENT: Literal["local", "production"] = "production"
    PROJECT_NAME: str = "FastAPI Full Stack Production"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
    VITE_API_BASE_URL: str = "/api"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )
