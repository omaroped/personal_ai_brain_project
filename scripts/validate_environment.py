#!/usr/bin/env python3
# MODULE: Environment validator for Python, services, models, and writable directories.
"""Validate the local runtime contract for the Personal AI Brain."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

import httpx

import config


def _check_python() -> tuple[bool, str]:
    expected = Path(".python-version").read_text(encoding="utf-8").strip() if Path(".python-version").exists() else "3.10"
    actual = platform.python_version()
    return actual.startswith(expected), f"python expected={expected} actual={actual}"


def _check_service(url: str, name: str) -> tuple[bool, str]:
    try:
        response = httpx.get(url, timeout=3.0)
        return response.status_code == 200, f"{name} status={response.status_code} url={url}"
    except Exception as exc:
        return False, f"{name} unreachable: {exc}"


def _check_path(path: Path, name: str) -> tuple[bool, str]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True, f"{name} writable={path}"
    except Exception as exc:
        return False, f"{name} not writable: {path} ({exc})"


def main() -> int:
    checks = [
        _check_python(),
        (_check_service(f"{config.OLLAMA_BASE_URL}/api/tags", "ollama")),
        (_check_service(f"{config.LETTA_BASE_URL}/v1/health/", "letta")),
        _check_path(config.DATA_DIR, "data_dir"),
        _check_path(config.VECTORDB_DIR, "vectordb_dir"),
        _check_path(config.LOGS_DIR, "logs_dir"),
    ]

    if not os.environ.get("VIRTUAL_ENV"):
        checks.append((False, "venv not active"))
    else:
        checks.append((True, f"venv active={os.environ['VIRTUAL_ENV']}"))

    all_ok = True
    for ok, detail in checks:
        prefix = "OK" if ok else "FAIL"
        print(f"[{prefix}] {detail}")
        all_ok = all_ok and ok
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
