# MODULE: Tests for vector-store helper methods and search-result shaping logic.
"""Tests for vector store helper logic."""

from __future__ import annotations

from src.ingestion.vector_store import VectorStore


def test_rrf_merge_basic() -> None:
    """RRF merge should combine and rank results from vector and text searches."""
    store = VectorStore.__new__(VectorStore)
    vector_results = [{"id": "a", "text": "apple"}, {"id": "b", "text": "banana"}]
    text_results = [{"id": "b", "text": "banana"}, {"id": "c", "text": "cherry"}]

    merged = store._rrf_merge(vector_results, text_results, k=60)

    assert len(merged) <= 3
    ids = [res["id"] for res in merged]
    assert "b" in ids
    assert "a" in ids
    assert "c" in ids


def test_rrf_merge_empty() -> None:
    """RRF merge should handle empty input lists gracefully."""
    store = VectorStore.__new__(VectorStore)
    assert store._rrf_merge([], [], k=60) == []

    results = [{"id": "a"}]
    assert store._rrf_merge(results, [], k=60) == [{"id": "a", "_rrf_score": 1 / 61}]
    assert store._rrf_merge([], results, k=60) == [{"id": "a", "_rrf_score": 1 / 61}]


def test_to_search_result_mapping() -> None:
    """Internal row mapping should produce the expected typed search result."""
    store = VectorStore.__new__(VectorStore)
    row = {
        "text": "sample text",
        "display_text": "[Source: test.pdf]\\nsample text",
        "source_file": "test.pdf",
        "page_number": 3,
        "section": "Intro",
        "domain": "ai_tech",
        "_distance": 0.1,
    }

    res = store._to_search_result(row)
    assert res.text == "sample text"
    assert res.display_text.startswith("[Source: test.pdf]")
    assert res.source_file == "test.pdf"
    assert res.page_number == 3
    assert res.section == "Intro"
    assert res.domain == "ai_tech"
    assert 0 < res.score < 1
