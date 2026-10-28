"""Zero-dependency unit test suite validating core application behaviors.

Design by Contract:
- Pre-conditions: Executable in pure Python standard library with no external dependencies.
- Post-conditions: All assertions pass deterministically in sub-second duration.
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from mainframe_template.config import Settings, get_settings
from mainframe_template.main import create_app


class TestConfigUnit(unittest.TestCase):
    """Unit tests for configuration loading and validation."""

    def test_default_settings(self) -> None:
        """Verify default configuration values match intended schema defaults."""
        with patch.dict(os.environ, {}, clear=True):
            settings: Settings = get_settings()
            self.assertEqual(settings.app_name, "mainframe-service")
            self.assertEqual(settings.app_env, "preview")
            self.assertEqual(settings.port, 8000)
            self.assertEqual(settings.log_level, "INFO")
            self.assertEqual(settings.version, "0.1.0")

    def test_environment_override(self) -> None:
        """Verify environment variables correctly override configuration fields."""
        overrides = {
            "APP_NAME": "custom-idea",
            "APP_ENV": "production",
            "PORT": "9090",
            "LOG_LEVEL": "DEBUG",
            "APP_VERSION": "1.2.3",
        }
        with patch.dict(os.environ, overrides, clear=True):
            settings: Settings = get_settings()
            self.assertEqual(settings.app_name, "custom-idea")
            self.assertEqual(settings.app_env, "production")
            self.assertEqual(settings.port, 9090)
            self.assertEqual(settings.log_level, "DEBUG")
            self.assertEqual(settings.version, "1.2.3")


class TestAppFactoryUnit(unittest.TestCase):
    """Unit tests for application factory lifecycle."""

    def test_create_app_instance(self) -> None:
        """Verify create_app produces a valid callable application object."""
        application = create_app()
        self.assertTrue(callable(application))


if __name__ == "__main__":
    unittest.main()
