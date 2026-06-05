# MODULE: Print Python interpreter and environment diagnostics for local debugging.
"""Emit a readable snapshot of Python runtime details and environment variables."""

from __future__ import annotations

import os
import site
import sys


def print_env() -> None:
    """Print interpreter, package path, and environment diagnostics."""
    print(f"Python Interpreter: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print("\nSite Packages:")

    for path in site.getsitepackages():
        print(f"  - {path}")

    user_site = site.getusersitepackages()
    if user_site:
        print(f"  - {user_site} (user)")

    print("\nEnvironment Variables (Selected):")
    important_vars = ["PYTHONPATH", "VIRTUAL_ENV", "PATH", "PYTHONHOME"]
    for var in important_vars:
        print(f"  {var}: {os.environ.get(var, 'Not Set')}")

    print("\nAll Environment Variables:")
    for key, value in sorted(os.environ.items()):
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print_env()
