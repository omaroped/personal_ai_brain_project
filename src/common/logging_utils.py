# MODULE: Shared logging configuration helpers used across project subsystems.
"""Logging helpers for consistent application-wide configuration."""

from __future__ import annotations

import logging
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Dict

from config import LOG_FILE, LOG_LEVEL, ensure_directories

class JsonFormatter(logging.Formatter):
    """Custom formatter to output logs as structured JSON."""
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields passed in 'extra'
        if hasattr(record, "extra_data"):
            log_entry["extra"] = record.extra_data
            
        return json.dumps(log_entry, ensure_ascii=False)


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

    # Use standard format for console, JSON for file
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    json_formatter = JsonFormatter()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10_000_000, backupCount=5)
    file_handler.setLevel(level)
    file_handler.setFormatter(json_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
