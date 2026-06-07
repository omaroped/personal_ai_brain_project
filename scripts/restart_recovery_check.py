#!/usr/bin/env python3
# MODULE: Restart and recovery probe for API-visible service resilience.
"""Check that the API recovers cleanly after dependent service interruptions."""

from __future__ import annotations

import argparse
import time

import httpx

import config


def wait_for_status(url: str, timeout_seconds: float = 60.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=3.0)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(2.0)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=f"http://{config.FASTAPI_HOST}:{config.FASTAPI_PORT}/control/status")
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()

    ok = wait_for_status(args.url, timeout_seconds=args.timeout)
    print(f"recovered={ok} url={args.url}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
