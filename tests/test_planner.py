# MODULE: Unit tests for the Task Planner ReAct loop.
"""Tests for the TaskPlanner logic and ReAct loop."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
import pytest

from src.agents.planner import TaskPlanner
from src.agents.tools import BaseTool

class MockTool(BaseTool):
    name = "mock_tool"
    description = "A test tool."
    def run(self, **kwargs):
        return f"Result of mock_tool with {kwargs}"

def test_planner_dry_run():
    """Planner should return success message immediately in dry run mode."""
    planner = TaskPlanner(dry_run=True)
    result = planner.execute("Test goal")
    assert "Dry run" in result

@patch("src.agents.base.ollama.Client")
def test_planner_react_loop_success(mock_ollama_client):
    """Planner should execute tools and then return a final answer."""
    # 1. Setup mocks
    client_instance = mock_ollama_client.return_value
    
    # First response: tool_call
    # Second response: final_answer
    client_instance.chat.side_effect = [
        {
            "message": {
                "content": json.dumps({
                    "type": "tool_call",
                    "thought": "I need to check the vault.",
                    "tool": "search_vault",
                    "args": {"q": "test query"}
                })
            }
        },
        {
            "message": {
                "content": json.dumps({
                    "type": "final_answer",
                    "content": "Found the answer in the vault."
                })
            }
        }
    ]
    
    # 2. Setup planner with real tool registry (it contains search_vault stub)
    planner = TaskPlanner()
    # Mock the tool run to avoid real network call
    with patch("src.agents.tools.SearchVaultTool.run") as mock_run:
        mock_run.return_value = "Mock vault contents"
        
        result = planner.execute("Search for mechatronics")
        
        # 3. Assertions
        assert result == "Found the answer in the vault."
        assert client_instance.chat.call_count == 2
        mock_run.assert_called_once_with(q="test query")

@patch("src.agents.base.ollama.Client")
def test_planner_safety_gate_rejection(mock_ollama_client):
    """Planner should stop if the user rejects a tool action."""
    client_instance = mock_ollama_client.return_value
    
    # Plan asks for write_file (sensitive)
    client_instance.chat.side_effect = [
        {
            "message": {
                "content": json.dumps({
                    "type": "tool_call",
                    "thought": "I want to delete everything.",
                    "tool": "write_file",
                    "args": {"path": "root", "content": "empty"}
                })
            }
        },
        # Second response: final_answer after rejection
        {
            "message": {
                "content": json.dumps({
                    "type": "final_answer",
                    "content": "Action aborted."
                })
            }
        }
    ]
    
    planner = TaskPlanner()
    # Force rejection
    planner.gate.request = MagicMock(return_value=False)
    
    result = planner.execute("Write to file")
    
    assert result == "Action aborted."
    planner.gate.request.assert_called_once()
    assert client_instance.chat.call_count == 2

@patch("src.agents.base.ollama.Client")
def test_planner_delegation(mock_ollama_client):
    """Planner should be able to delegate tasks to sub-agents."""
    client_instance = mock_ollama_client.return_value
    
    # 1. Planner decides to delegate
    client_instance.chat.side_effect = [
        {
            "message": {
                "content": json.dumps({
                    "type": "tool_call",
                    "thought": "This is too complex for me, delegating.",
                    "tool": "delegate_task",
                    "args": {"task": "Sub-task", "context": {"data": 123}}
                })
            }
        },
        {
            "message": {
                "content": json.dumps({
                    "type": "final_answer",
                    "content": "All done via delegation."
                })
            }
        }
    ]
    
    # 2. Mock SubAgent run to avoid nested LLM calls
    with patch("src.agents.sub_agent.SubAgent.run") as mock_sub_run:
        mock_run_result = "Sub-agent finished successfully."
        mock_sub_run.return_value = mock_run_result
        
        planner = TaskPlanner()
        result = planner.execute("Complex goal")
        
        assert result == "All done via delegation."
        mock_sub_run.assert_called_once()
