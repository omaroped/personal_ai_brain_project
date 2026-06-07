# MODULE: Tests for explicit planner state machine transitions.
"""State machine tests for planner transition guards."""

from __future__ import annotations

import pytest

from src.agents.state_machine import PlannerState, PlannerStateMachine


def test_state_machine_allows_valid_transitions() -> None:
    machine = PlannerStateMachine()
    machine.transition(PlannerState.PLAN)
    machine.transition(PlannerState.SELECT_TOOL)
    machine.transition(PlannerState.EXECUTE)
    machine.transition(PlannerState.OBSERVE)
    machine.transition(PlannerState.PLAN)

    assert machine.current_state == PlannerState.PLAN
    assert machine.history == [
        PlannerState.ANALYZE,
        PlannerState.PLAN,
        PlannerState.SELECT_TOOL,
        PlannerState.EXECUTE,
        PlannerState.OBSERVE,
        PlannerState.PLAN,
    ]


def test_state_machine_blocks_invalid_transitions() -> None:
    machine = PlannerStateMachine()

    with pytest.raises(ValueError):
        machine.transition(PlannerState.EXECUTE)
