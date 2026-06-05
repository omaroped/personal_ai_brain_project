# MODULE: Shared logging configuration helpers used across project subsystems.
"""Logging helpers for consistent application-wide configuration."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from config import LOG_FILE, LOG_LEVEL, ensure_directories


def configure_logging(logger_name: str | None = None) -> logging.Logger:
    """Configure and return a logger with console and rotating file handlers.

    Parameters:
        logger_name: Optional logger name. If omitted, the root project logger is used.

    Returns:
        logging.Logger: The configured logger instance.
    """
    ensure_directories()

    logger = logging.getLogger(logger_name or "personal_ai_brain")
    if logger.handlers:
        return logger

    level = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
