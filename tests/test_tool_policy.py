# MODULE: Tests for tool safety classification and confirmation policies.
"""Tool policy tests for Phase 6 safety hardening."""

from __future__ import annotations

from unittest.mock import patch

from src.agents.confirmation import ConfirmationGate
from src.agents.tool_policy import ToolRiskClass, get_tool_policy, get_tool_risk


def test_tool_risk_classification() -> None:
    assert get_tool_risk("search_vault") == ToolRiskClass.READ_ONLY
    assert get_tool_risk("execute_command") == ToolRiskClass.DESTRUCTIVE
    assert get_tool_risk("browse_url") == ToolRiskClass.NETWORKED


def test_confirmation_gate_skips_read_only_tools() -> None:
    gate = ConfirmationGate()
    assert gate.request("search_vault", {"q": "memory"}) is True


def test_confirmation_gate_blocks_rejected_destructive_tool() -> None:
    gate = ConfirmationGate()
    with patch("builtins.input", return_value="n"):
        assert gate.request("execute_command", {"command": "rm -rf /"}) is False


def test_confirmation_gate_allows_destructive_tool_when_approved() -> None:
    gate = ConfirmationGate()
    with patch("builtins.input", return_value="y"):
        assert gate.request("execute_command", {"command": "echo hi"}) is True


def test_tool_policy_requires_confirmation_for_destructive_tools() -> None:
    policy = get_tool_policy("run_python")
    assert policy.requires_confirmation is True
    assert policy.audit_required is True
