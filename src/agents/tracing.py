# MODULE: Planner execution trace structures for think-act-observe runs.
"""Trace models for planner and sub-agent execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import uuid


@dataclass
class PlannerStepTrace:
    """One step in a planner execution trace."""

    step_index: int
    state: str
    decision_type: str
    thought: str
    tool_name: str | None = None
    tool_args: dict | None = None
    observation: str | None = None
    error: str | None = None


@dataclass
class PlannerExecutionTrace:
    """Structured trace of one planner or sub-agent run."""

    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ""
    goal: str = ""
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None
    outcome: str | None = None
    state_history: list[str] = field(default_factory=list)
    steps: list[PlannerStepTrace] = field(default_factory=list)

    def add_step(self, step: PlannerStepTrace) -> None:
        self.steps.append(step)

    def finish(self, outcome: str) -> None:
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.outcome = outcome

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=True)
