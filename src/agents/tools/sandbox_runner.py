# MODULE: Bytebot sandbox integration for secure tool execution.
"""Interface for running natural language tasks in an isolated Docker sandbox."""

from __future__ import annotations

import httpx
import logging
from typing import Any, Dict

from src.common.logging_utils import configure_logging
import config

LOGGER = configure_logging(__name__)

BYTEBOT_URL = "http://localhost:9992"

def run_task_in_bytebot(task_description: str, timeout_seconds: int = 120) -> str:
    """
    Send a natural language task to Bytebot and return the result.
    
    Bytebot handles: clicking, typing, browsing, file operations.
    Everything runs in an isolated Docker container.
    """
    LOGGER.info("Sending task to Bytebot: %s", task_description)
    try:
        response = httpx.post(
            f"{BYTEBOT_URL}/api/tasks",
            json={"task": task_description},
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        result = response.json().get("result", "Task completed.")
        LOGGER.info("Bytebot task finished.")
        return result
    except Exception as exc:
        LOGGER.error("Bytebot task failed: %s", exc)
        return f"Error executing task in sandbox: {exc}"

if __name__ == "__main__":
    # Test stub
    print(run_task_in_bytebot("Open google.com and tell me the title."))
