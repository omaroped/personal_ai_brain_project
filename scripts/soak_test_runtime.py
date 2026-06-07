#!/usr/bin/env python3
# MODULE: Long-run stability probe for the core API control plane.
"""Simple soak test for repeated health and control-plane calls."""

from __future__ import annotations

import time

import httpx

import config


def main(iterations: int = 120, sleep_seconds: float = 1.0) -> int:
    urls = [
        f"http://{config.FASTAPI_HOST}:{config.FASTAPI_PORT}/health",
        f"http://{config.FASTAPI_HOST}:{config.FASTAPI_PORT}/control/status",
    ]
    for index in range(iterations):
        for url in urls:
            response = httpx.get(url, timeout=5.0)
            response.raise_for_status()
        print(f"iteration={index + 1}/{iterations} ok")
        time.sleep(sleep_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
