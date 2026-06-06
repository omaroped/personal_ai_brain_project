# MODULE: Task Planner responsible for breaking down high-level goals into sub-tasks.
"""Planner Agent that converts natural language goals into a structured execution plan."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List
import ollama

from src.common.logging_utils import configure_logging
import config

LOGGER = configure_logging(__name__)

class TaskPlanner:
    """Agent that reasons about a goal and produces a list of discrete tasks."""

    def __init__(self, model: str = config.LOCAL_LLM_MODEL) -> None:
        self.model = model
        self.client = ollama.Client(host="http://127.0.0.1:11434")

    def plan(self, goal: str) -> List[Dict[str, Any]]:
        """
        Break down a user goal into a list of executable sub-tasks.
        """
        LOGGER.info("Generating plan for goal: '%s' using model %s", goal, self.model)
        
        system_prompt = (
            "You are a master Task Planner. Break down complex goals into a sequence of small, verifiable sub-tasks. "
            "Each sub-task must use one of: 'file_reader', 'web_search', 'python_executor', 'shell_command', 'brain_memory'. "
            "Respond ONLY with a JSON array of task objects. No thinking text."
        )

        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Goal: {goal}"},
                ],
                format="json",
                stream=False,
            )
            
            message_content = response.get("message", {}).get("content", "[]")
            LOGGER.debug("Raw Planner Response: %s", message_content)
            
            plan = json.loads(message_content)
            if not isinstance(plan, list):
                LOGGER.error("Planner returned non-list format: %s", message_content)
                return []
                
            LOGGER.info("Plan generated successfully with %d steps.", len(plan))
            return plan
            
        except Exception as exc:
            LOGGER.error("Failed to generate plan: %s", exc)
            return []

if __name__ == "__main__":
    planner = TaskPlanner()
    test_goal = "List the files in my vault."
    plan = planner.plan(test_goal)
    print(json.dumps(plan, indent=2))
