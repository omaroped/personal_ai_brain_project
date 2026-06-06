# MODULE: Human-in-the-loop confirmation for sensitive agent actions.
"""Confirmation gate for authorizing destructive or external agent operations."""

from __future__ import annotations

import logging
from typing import Any, Dict

from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)

class ConfirmationGate:
    """Displays a confirmation prompt before any destructive agent action."""

    # Set of tool names that ALWAYS require user approval
    ALWAYS_CONFIRM = {
        "write_file",
        "run_python",
        "shell_command",
        "send_email",
        "delete_file",
        "execute_script",
    }

    def __init__(self, auto_approve: bool = False) -> None:
        self.auto_approve = auto_approve

    def request(self, tool_name: str, args: Dict[str, Any], thought: str = "") -> bool:
        """
        Ask the user for permission to execute a tool.
        
        Returns:
            bool: True if approved, False if rejected.
        """
        if self.auto_approve:
            LOGGER.info("Auto-approving sensitive action: %s", tool_name)
            return True

        if tool_name not in self.ALWAYS_CONFIRM:
            return True

        print(f"\n{'='*60}")
        print(f"⚠️  AGENT ACTION REQUEST: {tool_name.upper()}")
        print(f"{'='*60}")
        if thought:
            print(f"THOUGHT: {thought}")
        print(f"ARGUMENTS:")
        for k, v in args.items():
            print(f"  - {k}: {v}")
        print(f"{'='*60}")
        
        try:
            choice = input("\nApprove this action? [y/N]: ").strip().lower()
            approved = choice == "y"
            if approved:
                LOGGER.info("User APPROVED action: %s", tool_name)
            else:
                LOGGER.warning("User REJECTED action: %s", tool_name)
            return approved
        except EOFError:
            # Fallback for non-interactive environments
            LOGGER.error("Interactive input not available. Rejecting sensitive action.")
            return False

if __name__ == "__main__":
    # Test gate
    gate = ConfirmationGate()
    res = gate.request("write_file", {"path": "test.txt", "content": "hello"}, "Saving a test file.")
    print(f"Result: {res}")
