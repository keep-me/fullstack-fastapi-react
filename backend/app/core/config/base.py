"""
Base settings class for the application.
"""

import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(
    os.path.dirname(os.path.abspath(__file__)),
).parent.parent.parent.parent


class BaseAppSettings(BaseSettings):
    """
    Base settings class with common configuration.
    """

    API_V1_STR: str = "/api/v1"
    PROJECT_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["local", "production"]
    SWAGGER_FAVICON_URL: str = "https://fastapi.tiangolo.com/img/favicon.png"

    BASE_DIR: Path = BASE_DIR

    @classmethod
    def get_config(cls, env_file: str | None = None) -> SettingsConfigDict:
        """
        Get configuration with optional environment file override.
        """
        env_files = [str(BASE_DIR / ".env")]
        if env_file:
            env_files.append(env_file)
        return SettingsConfigDict(
            env_file=env_files,
            env_ignore_empty=True,
            extra="ignore",
        )
