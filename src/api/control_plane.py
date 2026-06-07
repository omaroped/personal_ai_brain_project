# MODULE: Control-plane snapshot helpers for runtime health and subsystem state.
"""Helpers for building control-plane status responses."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from src.agents.planner import TaskPlanner
from src.api.ws_manager import ConnectionManager
from src.common.health import collect_core_health
from src.identity.manager import IdentityManager


@dataclass
class ControlPlaneSnapshot:
    """Serializable view of current runtime state."""

    health: list[dict]
    identity: dict
    voice: dict
    planner: dict


def build_control_plane_snapshot(
    identity_manager: IdentityManager,
    ws_manager: ConnectionManager,
    task_planner: TaskPlanner,
) -> ControlPlaneSnapshot:
    """Collect a runtime snapshot for operational visibility."""
    return ControlPlaneSnapshot(
        health=[asdict(status) for status in collect_core_health()],
        identity=identity_manager.health(),
        voice=ws_manager.get_voice_state(),
        planner=task_planner.get_runtime_status(),
    )
