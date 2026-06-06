# MODULE: Sub-Agent for executing isolated, focused tasks.
"""Sub-Agent component for parallel or context-limited task execution."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from src.common.logging_utils import configure_logging
from src.agents.base import BaseAgent
import config

LOGGER = configure_logging(__name__)

class SubAgent(BaseAgent):
    """Agent that runs a single focused task with a fresh context window."""

    def __init__(
        self, 
        task: str, 
        context: Dict[str, Any], 
        allowed_tools: List[str] | None = None,
        model: str = config.LOCAL_LLM_MODEL,
        dry_run: bool = False
    ) -> None:
        """
        Initialize the sub-agent.
        
        Parameters:
            task: The specific task to accomplish.
            context: Data provided by the planner (metadata, search results, etc.)
            allowed_tools: Optional whitelist of tool names this sub-agent can use.
        """
        super().__init__(model=model, dry_run=dry_run, max_steps=5)
        self.task = task
        self.context = context
        self.allowed_tools = allowed_tools

    def run(self) -> str:
        """Execute the assigned task and return a summary."""
        tool_spec = self.tool_registry.get_prompt_specification()
        if self.allowed_tools:
            # Filter prompt spec to only allowed tools
            specs = []
            for tool in self.tool_registry.list_tools():
                if tool.name in self.allowed_tools:
                    specs.append(f"- {tool.name}: {tool.description}")
            tool_spec = "\n".join(specs)

        system_prompt = (
            "You are a specialized Sub-Agent. Your goal is to complete a specific sub-task.\n"
            f"Current Task: {self.task}\n"
            f"Context Data: {self.context}\n\n"
            "For each step, respond ONLY with JSON in one of two formats:\n\n"
            "Format A — use a tool:\n"
            '{"type": "tool_call", "thought": "why I\'m doing this", "tool": "tool_name", "args": {...}}\n\n'
            "Format B — done:\n"
            '{"type": "final_answer", "content": "summary of what was accomplished"}\n\n'
            f"Available tools:\n{tool_spec}\n\n"
            "Rules:\n"
            "1. Focus ONLY on the assigned sub-task.\n"
            "2. Stop at 5 steps maximum.\n"
            "3. Respond ONLY with raw JSON."
        )
        
        return self.run_loop(system_prompt, self.task)

if __name__ == "__main__":
    # Test sub-agent
    agent = SubAgent(
        task="Summarize this text: 'The robot arm moved smoothly.'",
        context={"note": "Initial test run"},
        dry_run=True
    )
    res = agent.run()
    print(f"Sub-Agent Result: {res}")
