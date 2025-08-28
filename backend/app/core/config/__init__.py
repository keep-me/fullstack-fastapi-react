"""
Configuration settings for the application.
"""

import os
from typing import Union

from app.core.exceptions import ConfigError

from .local import LocalSettings
from .production import ProductionSettings

SettingsType = Union[LocalSettings, ProductionSettings]


def get_settings() -> SettingsType:
    """
    Get appropriate settings based on environment.
    """
    environment = os.getenv("ENVIRONMENT", "local").lower()

    env_settings_map: dict[str, type[SettingsType]] = {
        "local": LocalSettings,
        "production": ProductionSettings,
    }

    settings_class = env_settings_map.get(environment)

    if not settings_class:
        raise ConfigError(
            f"Invalid environment: {environment}. "
            f"Must be one of: {list(env_settings_map.keys())}",
        )

    settings = settings_class()

    if hasattr(settings, "validate_settings"):
        settings.validate_settings()

    return settings


settings = get_settings()
