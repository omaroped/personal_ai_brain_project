# MODULE: Explicit planner state machine definitions and guarded transitions.
"""Planner state model used by the agency layer."""

from __future__ import annotations

from dataclasses import dataclass, field


class PlannerState:
    """Canonical planner execution states."""

    ANALYZE = "analyze"
    PLAN = "plan"
    SELECT_TOOL = "select_tool"
    REQUEST_CONFIRMATION = "request_confirmation"
    EXECUTE = "execute"
    OBSERVE = "observe"
    RECOVER = "recover"
    FINISH = "finish"
    ABORT = "abort"


ALLOWED_STATE_TRANSITIONS = {
    PlannerState.ANALYZE: {PlannerState.PLAN, PlannerState.ABORT},
    PlannerState.PLAN: {PlannerState.SELECT_TOOL, PlannerState.FINISH, PlannerState.ABORT},
    PlannerState.SELECT_TOOL: {PlannerState.REQUEST_CONFIRMATION, PlannerState.EXECUTE, PlannerState.RECOVER},
    PlannerState.REQUEST_CONFIRMATION: {PlannerState.EXECUTE, PlannerState.ABORT, PlannerState.RECOVER},
    PlannerState.EXECUTE: {PlannerState.OBSERVE, PlannerState.RECOVER, PlannerState.ABORT},
    PlannerState.OBSERVE: {PlannerState.PLAN, PlannerState.FINISH, PlannerState.RECOVER},
    PlannerState.RECOVER: {PlannerState.PLAN, PlannerState.ABORT},
    PlannerState.FINISH: set(),
    PlannerState.ABORT: set(),
}


@dataclass
class PlannerStateMachine:
    """Minimal guarded transition machine for planner runs."""

    current_state: str = PlannerState.ANALYZE
    history: list[str] = field(default_factory=lambda: [PlannerState.ANALYZE])

    def transition(self, next_state: str) -> None:
        """Move to the next state only if the transition is allowed."""
        allowed = ALLOWED_STATE_TRANSITIONS.get(self.current_state, set())
        if next_state not in allowed:
            raise ValueError(f"Invalid planner state transition: {self.current_state} -> {next_state}")
        self.current_state = next_state
        self.history.append(next_state)
