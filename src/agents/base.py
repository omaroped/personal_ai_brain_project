# MODULE: Base agent class with ReAct loop capabilities.
"""Shared logic for autonomous agents using the think-act-observe cycle."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List
import ollama

from src.common.logging_utils import configure_logging
from src.agents.state_machine import PlannerState, PlannerStateMachine
from src.agents.tool_policy import get_tool_policy
from src.agents.tracing import PlannerExecutionTrace, PlannerStepTrace
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
        self.last_trace: PlannerExecutionTrace | None = None

    def run_loop(self, system_prompt: str, initial_goal: str) -> str:
        """
        Execute the ReAct loop.
        """
        if self.dry_run:
            return f"Dry run completed for: {initial_goal[:30]}..."

        trace = PlannerExecutionTrace(agent_name=self.__class__.__name__, goal=initial_goal)
        self.last_trace = trace
        state_machine = PlannerStateMachine()
        trace.state_history = list(state_machine.history)
        history = [{"role": "user", "content": f"Goal: {initial_goal}"}]
        
        for step in range(self.max_steps):
            LOGGER.info("%s Loop - Step %d/%d", self.__class__.__name__, step + 1, self.max_steps)
            
            try:
                if step == 0:
                    state_machine.transition(PlannerState.PLAN)
                else:
                    state_machine.transition(PlannerState.PLAN)
                trace.state_history = list(state_machine.history)
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
                    state_machine.transition(PlannerState.FINISH)
                    trace.state_history = list(state_machine.history)
                    final_content = decision.get("content", "Goal completed.")
                    trace.add_step(
                        PlannerStepTrace(
                            step_index=step + 1,
                            state=state_machine.current_state,
                            decision_type="final_answer",
                            thought="Goal completed",
                            observation=final_content,
                        )
                    )
                    trace.finish(final_content)
                    return final_content
                
                if decision.get("type") == "tool_call":
                    state_machine.transition(PlannerState.SELECT_TOOL)
                    trace.state_history = list(state_machine.history)
                    tool_name = decision.get("tool")
                    tool_args = decision.get("args", {})
                    thought = decision.get("thought", "Executing tool...")
                    
                    LOGGER.info("Thinking: %s", thought)
                    
                    if not self.gate.request(tool_name, tool_args, thought):
                        state_machine.transition(PlannerState.REQUEST_CONFIRMATION)
                        trace.state_history = list(state_machine.history)
                        state_machine.transition(PlannerState.RECOVER)
                        trace.state_history = list(state_machine.history)
                        result = f"Action cancelled by user: {tool_name}"
                        trace.add_step(
                            PlannerStepTrace(
                                step_index=step + 1,
                                state=state_machine.current_state,
                                decision_type="tool_call",
                                thought=thought,
                                tool_name=tool_name,
                                tool_args=tool_args,
                                observation=result,
                            )
                        )
                        history.append({"role": "assistant", "content": content})
                        history.append({"role": "user", "content": f"Tool result: {result}"})
                        continue

                    tool = self.tool_registry.get_tool(tool_name)
                    if not tool:
                        state_machine.transition(PlannerState.RECOVER)
                        trace.state_history = list(state_machine.history)
                        result = f"Error: Tool '{tool_name}' not found."
                    else:
                        if get_tool_policy(tool_name).requires_confirmation:
                            state_machine.transition(PlannerState.REQUEST_CONFIRMATION)
                            trace.state_history = list(state_machine.history)
                        state_machine.transition(PlannerState.EXECUTE)
                        trace.state_history = list(state_machine.history)
                        LOGGER.info("Executing Tool: %s", tool_name)
                        result = str(tool.run(**tool_args))
                        state_machine.transition(PlannerState.OBSERVE)
                        trace.state_history = list(state_machine.history)
                    trace.add_step(
                        PlannerStepTrace(
                            step_index=step + 1,
                            state=state_machine.current_state,
                            decision_type="tool_call",
                            thought=thought,
                            tool_name=tool_name,
                            tool_args=tool_args,
                            observation=result,
                        )
                    )
                    
                    history.append({"role": "assistant", "content": content})
                    history.append({"role": "user", "content": f"Observation from {tool_name}: {result}"})
                
                else:
                    state_machine.transition(PlannerState.RECOVER)
                    trace.state_history = list(state_machine.history)
                    trace.add_step(
                        PlannerStepTrace(
                            step_index=step + 1,
                            state=state_machine.current_state,
                            decision_type="invalid_response",
                            thought="Model returned invalid decision format",
                            error="Use tool_call or final_answer.",
                        )
                    )
                    history.append({"role": "user", "content": "Error: Use tool_call or final_answer."})

            except Exception as exc:
                LOGGER.error("Step %d failed: %s", step + 1, exc)
                try:
                    state_machine.transition(PlannerState.RECOVER)
                    state_machine.transition(PlannerState.ABORT)
                except Exception:
                    pass
                trace.state_history = list(state_machine.history)
                trace.add_step(
                    PlannerStepTrace(
                        step_index=step + 1,
                        state=state_machine.current_state,
                        decision_type="exception",
                        thought="Planner step raised an exception",
                        error=str(exc),
                    )
                )
                trace.finish(f"Agent failed at step {step + 1}: {exc}")
                return f"Agent failed at step {step + 1}: {exc}"

        outcome = f"Agent reached maximum steps ({self.max_steps}) without finishing."
        try:
            state_machine.transition(PlannerState.ABORT)
        except Exception:
            pass
        trace.state_history = list(state_machine.history)
        trace.finish(outcome)
        return outcome
