# MODULE: Phase 6 runtime hardening tests for voice protocol, identity routing, planner traces, and control plane.
"""Tests for Phase 6 runtime boundary hardening work."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from src.agents.planner import TaskPlanner
from src.api.control_plane import build_control_plane_snapshot
from src.api.ws_manager import ConnectionManager
from src.identity.manager import IdentityManager
from src.voice.protocol import (
    TranscriptEvent,
    TTSResponseEvent,
    VoiceMessageType,
    VoiceStatus,
    parse_voice_message,
)


def test_voice_protocol_roundtrip_serialization() -> None:
    """Voice IPC messages should serialize and parse with stable metadata."""
    event = TranscriptEvent(text="hello brain", detected_language="en")
    payload = parse_voice_message(event.to_json())

    assert payload["type"] == VoiceMessageType.TRANSCRIPT
    assert payload["text"] == "hello brain"
    assert payload["detected_language"] == "en"
    assert payload["trace_id"]
    assert payload["protocol_version"] == "1.0"


def test_tts_response_reuses_trace_id() -> None:
    """The response back to the daemon should preserve the inbound trace ID."""
    response = TTSResponseEvent(text="ready", trace_id="trace-123")
    payload = parse_voice_message(response.to_json())

    assert payload["type"] == VoiceMessageType.TTS_RESPONSE
    assert payload["trace_id"] == "trace-123"
    assert payload["status"] == VoiceStatus.SPEAKING


def test_identity_manager_prefers_openclaw_when_available() -> None:
    """Successful OpenClaw responses should short-circuit fallback providers."""
    openclaw = MagicMock()
    openclaw.send_message.return_value = "Cloud reply"
    letta = MagicMock()

    manager = IdentityManager(letta_agent=letta, openclaw_agent=openclaw)
    response = manager.respond("hello")

    assert response.text == "Cloud reply"
    assert response.provider == "openclaw"
    letta.send_message.assert_not_called()


def test_identity_manager_falls_back_to_letta_on_openclaw_error() -> None:
    """OpenClaw failures should fall back to Letta cleanly."""
    openclaw = MagicMock()
    openclaw.send_message.return_value = "Error: OpenClaw execution failed."
    letta = MagicMock()
    letta.send_message.return_value = "Letta fallback reply"

    manager = IdentityManager(letta_agent=letta, openclaw_agent=openclaw)
    response = manager.respond("hello")

    assert response.text == "Letta fallback reply"
    assert response.provider == "letta"
    assert response.used_fallback is True


@patch("src.agents.base.ollama.Client")
def test_planner_records_execution_trace(mock_ollama_client: MagicMock) -> None:
    """Planner runs should leave a structured execution trace behind."""
    client_instance = mock_ollama_client.return_value
    client_instance.chat.side_effect = [
        {
            "message": {
                "content": json.dumps(
                    {
                        "type": "tool_call",
                        "thought": "I should search first.",
                        "tool": "search_vault",
                        "args": {"q": "memory"},
                    }
                )
            }
        },
        {
            "message": {
                "content": json.dumps(
                    {
                        "type": "final_answer",
                        "content": "I found relevant information.",
                    }
                )
            }
        },
    ]

    planner = TaskPlanner()
    with patch("src.agents.tools.SearchVaultTool.run", return_value="vault result"):
        result = planner.execute("Find memory notes")

    assert result == "I found relevant information."
    assert planner.last_trace is not None
    assert planner.last_trace.goal == "Find memory notes"
    assert len(planner.last_trace.steps) == 2
    assert planner.last_trace.steps[0].tool_name == "search_vault"
    assert planner.last_trace.outcome == "I found relevant information."


def test_control_plane_snapshot_exposes_voice_identity_and_planner_state() -> None:
    """Control-plane snapshots should aggregate subsystem state into one response."""
    identity = MagicMock()
    identity.health.return_value = {"letta_ready": True, "openclaw_available": True}
    planner = MagicMock()
    planner.get_runtime_status.return_value = {"agent": "TaskPlanner", "last_trace": None}
    ws_manager = ConnectionManager()
    ws_manager.current_voice_status = VoiceStatus.THINKING

    snapshot = build_control_plane_snapshot(identity, ws_manager, planner)

    assert snapshot.identity["letta_ready"] is True
    assert snapshot.voice["status"] == VoiceStatus.THINKING
    assert snapshot.planner["agent"] == "TaskPlanner"
    assert isinstance(snapshot.health, list)
