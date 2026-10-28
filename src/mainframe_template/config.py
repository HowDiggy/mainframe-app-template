"""Application configuration schema with environment fallback.

Design by Contract:
- Pre-conditions: System environment variables may provide configuration overrides.
- Post-conditions: Immutable settings instance returned with validated types.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Immutable application settings container.
    
    Attributes:
        app_name: Name of the application service.
        app_env: Deployment environment (e.g., development, preview, production).
        port: Listening port for the HTTP/ASGI server.
        log_level: Logging severity threshold.
        version: Application release version.
    """

    app_name: str
    app_env: str
    port: int
    log_level: str
    version: str


def get_settings() -> Settings:
    """Load application settings from environment variables.

    Docstring:
        Pre-conditions:
            None.
        Post-conditions:
            Returns a strictly typed Settings object populated from environment or defaults.
    """
    return Settings(
        app_name=os.getenv("APP_NAME", "mainframe-service"),
        app_env=os.getenv("APP_ENV", "preview"),
        port=int(os.getenv("PORT", "8000")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        version=os.getenv("APP_VERSION", "0.1.0"),
    )
