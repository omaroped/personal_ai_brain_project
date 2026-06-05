# MODULE: Tests for privacy routing, benchmark helpers, and vector-store foundation utilities.
"""Tests for independent foundation modules built in parallel."""

from __future__ import annotations

from src.api.privacy_router import (
    choose_model_route,
    is_cloud_allowed_for_domain,
    normalize_domain,
)
from src.common.benchmarks import BenchmarkRecorder, measure_call
from src.ingestion.vector_store import VECTOR_SCHEMA, default_table_paths


def test_normalize_domain_handles_empty_values() -> None:
    """Domain normalization should provide a stable fallback."""
    assert normalize_domain(None) == "unknown"
    assert normalize_domain("  ") == "unknown"
    assert normalize_domain("Religion") == "religion"


def test_sensitive_domains_remain_local() -> None:
    """Sensitive domains should not be cloud-routable by default."""
    assert is_cloud_allowed_for_domain("personal") is False
    decision = choose_model_route("religion", requested_route="cloud")
    assert decision.route == "local"
    assert decision.allow_cloud is False


def test_invalid_requested_route_falls_back_to_local() -> None:
    """Unknown route requests should fall back safely."""
    decision = choose_model_route("ai_tech", requested_route="sideways")
    assert decision.route == "local"
    assert "Unsupported route" in decision.reason


def test_benchmark_measurement_returns_value_and_duration() -> None:
    """The benchmark helper should return both function output and elapsed time."""
    result = measure_call("addition", lambda a, b: a + b, 2, 3)
    assert result.name == "addition"
    assert result.value == 5
    assert result.duration_ms >= 0


def test_benchmark_recorder_summarizes_results() -> None:
    """The benchmark recorder should expose a simple duration summary."""
    recorder = BenchmarkRecorder()
    recorder.record(measure_call("noop", lambda: None))
    summary = recorder.summary()
    assert "noop" in summary


def test_vector_schema_uses_expected_dimensions() -> None:
    """The vector schema should match the configured embedding dimensions."""
    vector_field = VECTOR_SCHEMA.field("vector")
    assert "fixed_size_list" in str(vector_field.type)
    assert "768" in str(vector_field.type)


def test_default_table_paths_expose_all_standard_tables() -> None:
    """The default logical table mapping should include all standard tables."""
    table_paths = default_table_paths()
    assert set(table_paths) == {"documents", "personal", "conversations", "errors"}
