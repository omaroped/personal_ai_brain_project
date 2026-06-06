# MODULE: Acceptance tests for Phase 2 core memory, review, extraction, and mistake tracking.
"""Phase 2 tests for the memory engine."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

import httpx

from src.memory.core_memory import CoreMemoryManager, LettaRuntime, LettaUnavailableError
from src.memory.daily_review import DailyReviewRunner
from src.memory.extractor import DailyReviewExtractor
from src.memory.mistake_tracker import MistakeTracker


def test_core_memory_file_is_created_with_required_schema(tmp_path: Path) -> None:
    """Missing core memory should be created with the Phase 2 schema."""
    manager = CoreMemoryManager(memory_path=tmp_path / "core_memory.json")

    payload = manager.load()

    assert payload == {
        "identity": {},
        "domains": [],
        "goals": [],
        "mistakes": [],
        "preferences": {},
        "active_projects": [],
        "last_reviewed_at": "",
    }


def test_update_section_preserves_unrelated_core_memory_keys(tmp_path: Path) -> None:
    """Updating one section should not remove unrelated data."""
    manager = CoreMemoryManager(memory_path=tmp_path / "core_memory.json")
    manager.save(
        {
            "identity": {"name": "Omar"},
            "domains": ["ai_tech"],
            "custom_notes": {"tone": "direct"},
        }
    )

    manager.update_section("goals", ["Finish Phase 2"])
    payload = manager.load()

    assert payload["identity"] == {"name": "Omar"}
    assert payload["domains"] == ["ai_tech"]
    assert payload["goals"] == ["Finish Phase 2"]
    assert payload["custom_notes"] == {"tone": "direct"}


def test_daily_review_writes_dated_markdown_file(tmp_path: Path) -> None:
    """Running the daily review should create a dated markdown log."""
    runner = DailyReviewRunner(logs_dir=tmp_path / "logs")
    runner.collect_inputs = lambda: {
        "changed_files": ["Updated src/memory/core_memory.py"],
        "learnings": ["Local-first memory needs deterministic summaries."],
        "blockers": ["Need to validate Letta health before sync."],
        "mistakes": ["Repeated mistake: skipping acceptance tests."],
        "priorities": ["Finish Phase 2 validation."],
    }

    review_path = runner.run(date(2026, 6, 6))

    assert review_path == tmp_path / "logs" / "2026-06-06.md"
    content = review_path.read_text(encoding="utf-8")
    assert "# Daily Review" in content
    assert "## Next Priorities" in content
    assert "Finish Phase 2 validation." in content


def test_extractor_turns_review_into_structured_updates(tmp_path: Path) -> None:
    """Daily review extraction should return durable structured updates."""
    review_path = tmp_path / "2026-06-06.md"
    review_path.write_text(
        "\n".join(
            [
                "# Daily Review",
                "",
                "- Learned that Docker runtime checks matter for AI infrastructure.",
                "- Repeated mistake: starting implementation without a stable foundation. learned verify health first",
                "- Next step: configure Letta and sync core memory",
            ]
        ),
        encoding="utf-8",
    )

    updates = DailyReviewExtractor().extract_updates(review_path)

    assert updates["goals"] == ["configure Letta and sync core memory"]
    assert updates["domains"] == ["ai_tech"]
    assert updates["mistakes"] == [
        {
            "context": "starting implementation without a stable foundation",
            "correction": "verify health first",
        }
    ]
    assert updates["last_reviewed_at"] == "2026-06-06"


def test_mistake_tracker_returns_relevant_prior_mistakes(tmp_path: Path) -> None:
    """The pre-task check should surface relevant previously logged mistakes."""
    tracker = MistakeTracker(storage_path=tmp_path / "mistakes.json")
    tracker.log_mistake(
        title="Skipped service health checks",
        context="Started Letta-dependent work before verifying container health.",
        fix="Check the Letta health endpoint before memory sync.",
        tags=["letta", "health", "runtime"],
    )
    tracker.log_mistake(
        title="Skipped service health checks",
        context="Repeated during memory work.",
        fix="Check the Letta health endpoint before memory sync.",
        tags=["memory"],
    )

    matches = tracker.pre_task_check("Set up Letta runtime health checks before sync")

    assert len(matches) == 1
    assert matches[0]["title"] == "Skipped service health checks"
    assert matches[0]["occurrences"] == 2
    assert "memory" in matches[0]["tags"]


def test_letta_sync_path_fails_clearly_when_service_is_down(tmp_path: Path) -> None:
    """Letta sync should raise a clear error instead of hanging silently."""
    manager = CoreMemoryManager(
        memory_path=tmp_path / "core_memory.json",
        letta_runtime=LettaRuntime(base_url="http://localhost:8283", agent_name="omar_brain"),
    )
    manager.ensure_schema()

    with patch("src.memory.core_memory.httpx.request", side_effect=httpx.ConnectError("Connection refused")):
        try:
            manager.sync_to_letta()
        except LettaUnavailableError as exc:
            assert "Letta request failed" in str(exc)
            assert "Connection refused" in str(exc)
        else:
            raise AssertionError("Expected LettaUnavailableError when service is down")


def test_letta_runtime_creates_agent_when_missing() -> None:
    """The runtime helper should create the configured agent if it does not exist."""
    responses = [
        httpx.Response(200, request=httpx.Request("GET", "http://localhost:8283/health")),
        httpx.Response(200, request=httpx.Request("GET", "http://localhost:8283/v1/agents"), json=[]),
        httpx.Response(
            200,
            request=httpx.Request("POST", "http://localhost:8283/v1/agents"),
            json={"id": "agent-123", "name": "omar_brain"},
        ),
    ]

    with patch("src.memory.core_memory.httpx.request", side_effect=responses):
        agent = LettaRuntime(base_url="http://localhost:8283", agent_name="omar_brain").ensure_agent()

    assert agent["id"] == "agent-123"
    assert agent["name"] == "omar_brain"
