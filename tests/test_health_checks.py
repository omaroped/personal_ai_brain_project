# MODULE: Tests for HTTP and filesystem health-check helpers with mocked dependencies.
"""Tests for the health check utilities with mocking."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import httpx
import pytest

from src.common.health import check_http_service, check_path_ready, collect_core_health


def test_check_path_ready() -> None:
    """Path check should return ok for existing paths."""
    # Test existing
    status = check_path_ready("root", Path("/home/omar"))
    assert status.ok is True
    
    # Test missing
    status = check_path_ready("missing", Path("/non/existent/path/999"))
    assert status.ok is False


@patch("httpx.get")
def test_check_http_service_success(mock_get: MagicMock) -> None:
    """HTTP check should return ok for 200 responses."""
    mock_get.return_value = MagicMock(status_code=200)
    mock_get.return_value.raise_for_status = MagicMock()
    
    status = check_http_service("test", "http://localhost")
    assert status.ok is True
    assert "HTTP 200" in status.detail


@patch("httpx.get")
def test_check_http_service_failure(mock_get: MagicMock) -> None:
    """HTTP check should return failure for exceptions."""
    mock_get.side_effect = httpx.ConnectError("Connection refused")
    
    status = check_http_service("test", "http://localhost")
    assert status.ok is False
    assert "Connection refused" in status.detail


@patch("src.common.health.check_http_service")
@patch("src.common.health.check_path_ready")
def test_collect_core_health(mock_path: MagicMock, mock_http: MagicMock) -> None:
    """Collect health should aggregate multiple checks."""
    mock_http.return_value = MagicMock(ok=True, name="http")
    mock_path.return_value = MagicMock(ok=True, name="path")
    
    results = collect_core_health()
    assert len(results) == 3  # ollama, letta, vectordb_dir
    assert all(r.ok for r in results)
