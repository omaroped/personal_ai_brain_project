# MODULE: Tests for shared logging configuration helpers and logger behavior.
"""Tests for logging configuration utilities."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from src.common.logging_utils import configure_logging


def test_configure_logging_idempotency() -> None:
    """Configuring the same logger twice should return the same instance without adding handlers."""
    logger1 = configure_logging("test_logger_unique")
    count1 = len(logger1.handlers)
    
    logger2 = configure_logging("test_logger_unique")
    count2 = len(logger2.handlers)
    
    assert logger1 is logger2
    assert count1 == count2
    assert count1 > 0


def test_configure_logging_format() -> None:
    """Logger should have handlers with the expected format."""
    logger = configure_logging("test_format")
    for handler in logger.handlers:
        assert handler.formatter is not None
        # Check for standard parts of the format string
        fmt = handler.formatter._fmt
        assert "%(asctime)s" in fmt
        assert "%(levelname)s" in fmt
        assert "%(message)s" in fmt


def test_logger_level_setting() -> None:
    """Logger should respect the default level from config."""
    # This indirectly tests config import and getattr
    logger = configure_logging("test_level")
    assert logger.level == logging.INFO  # Default in config.py is usually INFO
