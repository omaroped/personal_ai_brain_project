# MODULE: Tests for query.py 'count' command.
"""Tests for the count command in the query CLI."""

from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from query import app

runner = CliRunner()


def test_count_command_all() -> None:
    """The count command should show counts for all tables by default."""
    with patch("src.ingestion.vector_store.VectorStore.count", side_effect=[10, 20]):
        result = runner.invoke(app, ["count"])
    
    assert result.exit_code == 0
    assert "Vector Store Counts" in result.stdout
    assert "documents" in result.stdout
    assert "10" in result.stdout
    assert "personal" in result.stdout
    assert "20" in result.stdout
    assert "total" in result.stdout
    assert "30" in result.stdout


def test_count_command_specific_table() -> None:
    """The count command should show count for a specific table."""
    with patch("src.ingestion.vector_store.VectorStore.count", return_value=15):
        result = runner.invoke(app, ["count", "--table", "documents"])
    
    assert result.exit_code == 0
    assert "documents" in result.stdout
    assert "15" in result.stdout
    assert "personal" not in result.stdout


def test_count_command_invalid_table() -> None:
    """The count command should fail for an invalid table name."""
    result = runner.invoke(app, ["count", "--table", "invalid"])
    assert result.exit_code != 0
    assert "Invalid value" in result.stdout or "table must be one of" in result.stdout
