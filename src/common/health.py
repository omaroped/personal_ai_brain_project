# MODULE: Service health-check helpers for Ollama, Letta, and core local storage readiness.
"""Health-check helpers for local services and project directories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import httpx

from config import LETTA_BASE_URL, OLLAMA_BASE_URL, VECTORDB_DIR


@dataclass
class HealthStatus:
    """Represents the health of one service or local dependency.

    Parameters:
        name: Human-readable service name.
        ok: Whether the dependency is healthy.
        detail: Extra diagnostic detail.
    """

    name: str
    ok: bool
    detail: str


def check_http_service(name: str, url: str, timeout: float = 3.0) -> HealthStatus:
    """Check whether an HTTP service responds successfully.

    Parameters:
        name: Human-readable service name.
        url: Full URL to query.
        timeout: Request timeout in seconds.

    Returns:
        HealthStatus: Result of the health check.
    """
    try:
        response = httpx.get(url, timeout=timeout)
        response.raise_for_status()
        return HealthStatus(name=name, ok=True, detail=f"HTTP {response.status_code}")
    except httpx.HTTPError as exc:
        return HealthStatus(name=name, ok=False, detail=str(exc))


def check_path_ready(name: str, path: Path) -> HealthStatus:
    """Check whether a required filesystem path exists.

    Parameters:
        name: Human-readable path label.
        path: Filesystem path to inspect.

    Returns:
        HealthStatus: Result of the readiness check.
    """
    if path.exists():
        return HealthStatus(name=name, ok=True, detail=str(path))
    return HealthStatus(name=name, ok=False, detail=f"Missing path: {path}")


def collect_core_health() -> list[HealthStatus]:
    """Collect health results for the core local dependencies.

    Returns:
        list[HealthStatus]: Health results for the main services and directories.
    """
    return [
        check_http_service("ollama", f"{OLLAMA_BASE_URL}/api/tags"),
        check_http_service("letta", f"{LETTA_BASE_URL}/v1/health/"),
        check_path_ready("vectordb_dir", VECTORDB_DIR),
    ]
