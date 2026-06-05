# MODULE: Operational script to verify the health of local services and filesystem.
"""Checks Ollama, Letta, and core directories to ensure the system is ready."""

from __future__ import annotations

import logging
import sys

# Ensure project root is in path if running directly
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.common.health import collect_core_health
from src.common.logging_utils import configure_logging

def main():
    """Run health checks and print a human-readable summary."""
    # Use internal logger for trace but print for the user
    logger = configure_logging("verify_services")
    logger.info("Starting service verification...")
    
    print("\n=== Personal AI Brain Service Verification ===\n")
    
    all_ok = True
    statuses = collect_core_health()
    
    for status in statuses:
        icon = "✅" if status.ok else "❌"
        print(f"{icon} {status.name.upper():<15} | Status: {'OK' if status.ok else 'FAILED':<6} | Detail: {status.detail}")
        if not status.ok:
            all_ok = False
            
    print("\n" + "=" * 47)
    if all_ok:
        print("\n✨ ALL SYSTEMS READY ✨\n")
        sys.exit(0)
    else:
        print("\n⚠️ SOME SERVICES ARE NOT RESPONDING ⚠️")
        print("Check CLAUDE.md for startup instructions.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
