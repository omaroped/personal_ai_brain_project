# MODULE: Base agent class with ReAct loop capabilities.
"""Shared logic for autonomous agents using the think-act-observe cycle."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List
import ollama

from src.common.logging_utils import configure_logging
from src.agents.tools import registry, ToolRegistry
from src.agents.confirmation import ConfirmationGate
import config

LOGGER = configure_logging(__name__)

class BaseAgent:
    """Base class for agents using a ReAct execution loop."""

    def __init__(
        self, 
        model: str = config.LOCAL_LLM_MODEL, 
        dry_run: bool = False,
        max_steps: int = 5,
        tool_registry: ToolRegistry | None = None
    ) -> None:
        self.model = model
        self.client = ollama.Client(host="http://127.0.0.1:11434")
        self.dry_run = dry_run
        self.max_steps = max_steps
        self.tool_registry = tool_registry or registry
        self.gate = ConfirmationGate()

    def run_loop(self, system_prompt: str, initial_goal: str) -> str:
        """
        Execute the ReAct loop.
        """
        if self.dry_run:
            return f"Dry run completed for: {initial_goal[:30]}..."

        history = [{"role": "user", "content": f"Goal: {initial_goal}"}]
        
        for step in range(self.max_steps):
            LOGGER.info("%s Loop - Step %d/%d", self.__class__.__name__, step + 1, self.max_steps)
            
            try:
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *history
                    ],
                    format="json",
                    stream=False,
                )
                
                content = response.get("message", {}).get("content", "{}")
                decision = json.loads(content)
                
                if decision.get("type") == "final_answer":
                    return decision.get("content", "Goal completed.")
                
                if decision.get("type") == "tool_call":
                    tool_name = decision.get("tool")
                    tool_args = decision.get("args", {})
                    thought = decision.get("thought", "Executing tool...")
                    
                    LOGGER.info("Thinking: %s", thought)
                    
                    if not self.gate.request(tool_name, tool_args, thought):
                        result = f"Action cancelled by user: {tool_name}"
                        history.append({"role": "assistant", "content": content})
                        history.append({"role": "user", "content": f"Tool result: {result}"})
                        continue

                    tool = self.tool_registry.get_tool(tool_name)
                    if not tool:
                        result = f"Error: Tool '{tool_name}' not found."
                    else:
                        LOGGER.info("Executing Tool: %s", tool_name)
                        result = str(tool.run(**tool_args))
                    
                    history.append({"role": "assistant", "content": content})
                    history.append({"role": "user", "content": f"Observation from {tool_name}: {result}"})
                
                else:
                    history.append({"role": "user", "content": "Error: Use tool_call or final_answer."})

            except Exception as exc:
                LOGGER.error("Step %d failed: %s", step + 1, exc)
                return f"Agent failed at step {step + 1}: {exc}"

        return f"Agent reached maximum steps ({self.max_steps}) without finishing."
