# MODULE: Task Planner with ReAct loop for autonomous goal execution.
"""Autonomous Planner Agent that completes goals using a think-act-observe cycle."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from src.common.logging_utils import configure_logging
from src.agents.base import BaseAgent
import config

LOGGER = configure_logging(__name__)

class TaskPlanner(BaseAgent):
    """Agent that reasons about a goal and executes tools in a ReAct loop."""

    def __init__(self, model: str = config.LOCAL_LLM_MODEL, dry_run: bool = False) -> None:
        super().__init__(model=model, dry_run=dry_run, max_steps=10)

    def execute(self, goal: str) -> str:
        """
        Main execution loop for completing a user goal.
        """
        system_prompt = (
            "You are a master Task Planner. Your job is to complete a user goal using tools.\n\n"
            "For each step, respond ONLY with JSON in one of two formats:\n\n"
            "Format A — use a tool:\n"
            '{"type": "tool_call", "thought": "why I\'m doing this", "tool": "tool_name", "args": {...}}\n\n'
            "Format B — done:\n"
            '{"type": "final_answer", "content": "what was accomplished"}\n\n'
            f"Available tools:\n{self.tool_registry.get_prompt_specification()}\n\n"
            "Rules:\n"
            "1. Always search_vault BEFORE assuming knowledge.\n"
            "2. Stop at 10 steps maximum.\n"
            "3. Respond ONLY with raw JSON. No markdown blocks."
        )
        return self.run_loop(system_prompt, goal)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("goal", type=str, help="The goal to execute.")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing.")
    args = parser.parse_args()

    planner = TaskPlanner(dry_run=args.dry_run)
    final_result = planner.execute(args.goal)
    print(f"\n--- FINAL RESULT ---\n{final_result}")
