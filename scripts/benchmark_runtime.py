#!/usr/bin/env python3
# MODULE: Lightweight runtime benchmark harness for API and control-plane latency.
"""Measure core local runtime endpoints."""

from __future__ import annotations

import statistics
import time

import httpx

import config


def measure_get(url: str, runs: int = 5) -> dict:
    timings = []
    for _ in range(runs):
        start = time.perf_counter()
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        timings.append((time.perf_counter() - start) * 1000)
    return {
        "url": url,
        "mean_ms": round(statistics.mean(timings), 2),
        "p95_ms": round(max(timings), 2),
    }


def main() -> int:
    targets = [
        f"http://{config.FASTAPI_HOST}:{config.FASTAPI_PORT}/health",
        f"http://{config.FASTAPI_HOST}:{config.FASTAPI_PORT}/control/status",
        f"http://{config.FASTAPI_HOST}:{config.FASTAPI_PORT}/search?q=test&top_k=1",
    ]
    for target in targets:
        result = measure_get(target)
        print(f"{result['url']} mean={result['mean_ms']}ms p95={result['p95_ms']}ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
