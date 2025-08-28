"""
Configuration components for the application.
"""

import os
from datetime import timedelta
from typing import Any

from pydantic import EmailStr, PostgresDsn
from pydantic_settings import BaseSettings


class ServerSettings(BaseSettings):
    API_V1_STR: str
    SECRET_KEY: str
    BACKEND_CORS_ORIGINS: str = ""
    BACKEND_CORS_ORIGIN_REGEX: str = ""
    SERVER_HOST: str
    SERVER_PORT: int
    SERVER_WORKERS: int
    SERVER_RELOAD: bool
    FRONTEND_HOST: str = ""
    MAX_CONCURRENT_REQUESTS: int = 100
    MAX_REQUEST_TIME: int = 30
    RATE_LIMIT_PER_MINUTE: int = 30
    RATE_LIMIT_PER_SECOND: int = 5

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Parse CORS origins from string.
        """
        if not self.BACKEND_CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    @property
    def frontend_host_list(self) -> list[str]:
        """
        Parse frontend hosts from string.
        """
        if not self.FRONTEND_HOST:
            return []
        return [host.strip() for host in self.FRONTEND_HOST.split(",")]

    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.cors_origins_list] + [
            str(origin).rstrip("/") for origin in self.frontend_host_list
        ]


class DatabaseSettings(BaseSettings):
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_PORT: int = 5432
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 60
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False
    DB_ISOLATION_LEVEL: str = "READ COMMITTED"
    DB_CONNECTION_RETRY_MAX_TRIES: int = 3
    DB_CONNECTION_RETRY_WAIT_SECONDS: int = 1

    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            path=self.POSTGRES_DB,
        )


class RedisSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PASSWORD: str = ""
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_TIMEOUT: int = 5
    CACHE_EXPIRE_SECONDS: int = 86400


class AuthSettings(BaseSettings):
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_COOKIES_NAME: str = "refresh_token"
    MAX_REFRESH_SESSIONS: int = 5
    RESET_CODE_EXPIRE_MINUTES: int = 15
    COOKIE_SECURE: bool = True

    @property
    def ACCESS_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def REFRESH_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(minutes=self.REFRESH_TOKEN_EXPIRE_MINUTES)


class UserSettings(BaseSettings):
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_NAME: str


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"

    @property
    def FORMATTERS(self) -> dict[str, dict[str, Any]]:
        return {
            "console": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s (%(filename)s:%(lineno)d)",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        }

    @property
    def HANDLERS(self) -> dict[str, dict[str, Any]]:
        return {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
                "level": self.LOG_LEVEL,
                "stream": "ext://sys.stdout",
            },
        }

    @property
    def LOGGERS(self) -> dict[str, dict[str, Any]]:
        return {
            "app": {
                "handlers": ["console"],
                "level": self.LOG_LEVEL,
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": self.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": self.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": self.LOG_LEVEL,
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": os.getenv("DB_ECHO", "WARNING"),
                "propagate": False,
            },
        }

    @property
    def LOGGING_CONFIG(self) -> dict[str, Any]:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": self.FORMATTERS,
            "handlers": self.HANDLERS,
            "loggers": self.LOGGERS,
        }

    SENTRY_DSN: str | None = None


class RabbitMQSettings(BaseSettings):
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_DEFAULT_USER: str = "guest"
    RABBITMQ_DEFAULT_PASS: str = "guest"
    RABBITMQ_VHOST: str = "/"


class EmailSettings(BaseSettings):
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = "user"
    SMTP_PASSWORD: str = "password"
    EMAIL_FROM: str = "noreply@example.com"


class SecuritySettings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ALGORITHM: str = "HS256"

    ENABLE_RATE_LIMITING: bool = True
    ENABLE_LOAD_PROTECTION: bool = True
    ENABLE_CIRCUIT_BREAKER: bool = True


class LoadTestSettings(BaseSettings):
    """
    Settings for load testing configuration.
    """

    LOAD_TEST_HOST: str = "http://0.0.0.0:8000"
    LOAD_TEST_USERS: int = 10
    LOAD_TEST_SPAWN_RATE: int = 2
    LOAD_TEST_DURATION: str = "2m"
    LOAD_TEST_OUTPUT_DIR: str = "monitoring/load"
