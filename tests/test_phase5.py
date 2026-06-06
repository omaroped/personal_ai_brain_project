# MODULE: Acceptance tests for Phase 5 Agency & Proactivity components.
"""End-to-end and integration tests for the Agency Layer."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
import pytest

from src.agents.planner import TaskPlanner
from src.agents.sub_agent import SubAgent

@patch("src.agents.base.ollama.Client")
def test_full_agency_delegation_flow(mock_ollama):
    """Planner should delegate to SubAgent and reach a final answer."""
    client_instance = mock_ollama.return_value
    
    # Sequence of decisions
    client_instance.chat.side_effect = [
        # 1. Planner decides to delegate (Step 1)
        {
            "message": {
                "content": json.dumps({
                    "type": "tool_call",
                    "thought": "I will delegate this complex summary task.",
                    "tool": "delegate_task",
                    "args": {"task": "Summarize vault", "context": {}}
                })
            }
        },
        # 2. Sub-agent's decision (called via tool run INSIDE Step 1)
        {
            "message": {
                "content": json.dumps({
                    "type": "final_answer",
                    "content": "Sub-agent work complete."
                })
            }
        },
        # 3. Planner gives final answer (Step 2)
        {
            "message": {
                "content": json.dumps({
                    "type": "final_answer",
                    "content": "All documents summarized successfully."
                })
            }
        }
    ]
    
    planner = TaskPlanner()
    result = planner.execute("Summarize the whole vault")
    
    assert result == "All documents summarized successfully."
    # Total calls: 2 for planner, 1 for sub-agent = 3
    assert client_instance.chat.call_count == 3
