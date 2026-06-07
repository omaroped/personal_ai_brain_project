# MODULE: Tool safety classes and confirmation policy for agent capabilities.
"""Canonical policy model for agent tools."""

from __future__ import annotations

from dataclasses import dataclass


class ToolRiskClass:
    """Canonical tool safety categories."""

    READ_ONLY = "read_only"
    LOCAL_WRITE = "local_write"
    SYSTEM_CONTROL = "system_control"
    NETWORKED = "networked"
    DESTRUCTIVE = "destructive"


TOOL_RISK_BY_NAME = {
    "search_vault": ToolRiskClass.READ_ONLY,
    "read_file": ToolRiskClass.READ_ONLY,
    "send_notification": ToolRiskClass.SYSTEM_CONTROL,
    "delegate_task": ToolRiskClass.SYSTEM_CONTROL,
    "run_python": ToolRiskClass.DESTRUCTIVE,
    "browse_url": ToolRiskClass.NETWORKED,
    "execute_command": ToolRiskClass.DESTRUCTIVE,
    "capture_screen": ToolRiskClass.NETWORKED,
    "write_file": ToolRiskClass.LOCAL_WRITE,
    "delete_file": ToolRiskClass.DESTRUCTIVE,
    "shell_command": ToolRiskClass.DESTRUCTIVE,
    "send_email": ToolRiskClass.NETWORKED,
    "execute_script": ToolRiskClass.DESTRUCTIVE,
}


@dataclass(frozen=True)
class ToolPolicy:
    """Policy controls for one tool class."""

    requires_confirmation: bool
    audit_required: bool


POLICY_BY_RISK = {
    ToolRiskClass.READ_ONLY: ToolPolicy(requires_confirmation=False, audit_required=False),
    ToolRiskClass.LOCAL_WRITE: ToolPolicy(requires_confirmation=True, audit_required=True),
    ToolRiskClass.SYSTEM_CONTROL: ToolPolicy(requires_confirmation=False, audit_required=True),
    ToolRiskClass.NETWORKED: ToolPolicy(requires_confirmation=False, audit_required=True),
    ToolRiskClass.DESTRUCTIVE: ToolPolicy(requires_confirmation=True, audit_required=True),
}


def get_tool_risk(tool_name: str) -> str:
    """Return the configured risk class for a tool."""
    return TOOL_RISK_BY_NAME.get(tool_name, ToolRiskClass.SYSTEM_CONTROL)


def get_tool_policy(tool_name: str) -> ToolPolicy:
    """Return confirmation/audit policy for a tool name."""
    return POLICY_BY_RISK[get_tool_risk(tool_name)]
