# MODULE: Tests for query.py 'legacy mode' (direct question parsing).
"""Tests for the legacy mode in the query CLI where the first argument is a question."""

from __future__ import annotations

import sys
from unittest.mock import patch

from query import main


def test_legacy_mode_simple_question() -> None:
    """The CLI should accept a question as the first argument."""
    with patch.object(sys, "argv", ["query.py", "What is AI?"]):
        with patch("query.search") as mock_search:
            main()
            mock_search.assert_called_once_with(
                query_text="What is AI?",
                domain=None,
                table_name="all",
                mode="hybrid",
                top_k=5
            )


def test_legacy_mode_with_options() -> None:
    """The CLI should accept a question followed by options in legacy mode."""
    with patch.object(sys, "argv", ["query.py", "deep learning", "--domain", "tech", "--top", "10", "--mode", "vector", "--table", "documents"]):
        with patch("query.search") as mock_search:
            main()
            mock_search.assert_called_once_with(
                query_text="deep learning",
                domain="tech",
                table_name="documents",
                mode="vector",
                top_k=10
            )


def test_legacy_mode_known_command_goes_to_app() -> None:
    """Known commands should not trigger legacy mode and should go to Typer app."""
    with patch.object(sys, "argv", ["query.py", "health"]):
        with patch("query.app") as mock_app:
            main()
            mock_app.assert_called_once()


def test_legacy_mode_starts_with_dash_goes_to_app() -> None:
    """Arguments starting with dash should not trigger legacy mode."""
    with patch.object(sys, "argv", ["query.py", "--help"]):
        with patch("query.app") as mock_app:
            main()
            mock_app.assert_called_once()
