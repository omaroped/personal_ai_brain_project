# MODULE: Focused tests for query result rendering behavior.
"""Unit tests for human-readable query result rendering."""

from __future__ import annotations

from unittest.mock import patch

from query import _render_search_results
from src.ingestion.vector_store import SearchResult


def test_render_search_results_handles_empty_results() -> None:
    """Empty result sets should print a simple no-results message."""
    with patch("query.console.print") as mock_print:
        _render_search_results("memory", [])

    mock_print.assert_called_once_with("No results found.")


def test_render_search_results_prints_summary_and_table() -> None:
    """Non-empty results should print a summary followed by a table."""
    result = SearchResult(
        text="Working memory supports short-term retention.",
        display_text="[Source: Notes | Section: Working Memory | Page: 2]\nWorking memory supports short-term retention.",
        source_file="notes.md",
        page_number=2,
        section="Working Memory",
        domain="psychology",
        score=0.91,
    )

    with patch("query.console.print") as mock_print:
        _render_search_results("working memory", [("documents", result)])

    assert mock_print.call_count == 4
    assert mock_print.call_args_list[0].args[0] == 'Query: "working memory"'
    assert mock_print.call_args_list[1].args[0] == "Results from: documents table"
    assert mock_print.call_args_list[2].args[0] == "Sources: notes.md"
    rendered_table = mock_print.call_args_list[3].args[0]
    assert getattr(rendered_table, "title", "") == "Search Results: working memory"


def test_render_search_results_reports_multiple_tables() -> None:
    """Mixed table results should state that multiple tables contributed."""
    result = SearchResult(
        text="A short note.",
        display_text="[Source: Notes | Section: General | Page: 1]\nA short note.",
        source_file="notes.md",
        page_number=1,
        section="General",
        domain="general",
        score=0.5,
    )

    with patch("query.console.print") as mock_print:
        _render_search_results("note", [("documents", result), ("personal", result)])

    assert mock_print.call_args_list[1].args[0] == "Results from: multiple tables"
