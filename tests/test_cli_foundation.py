# MODULE: Tests for stable CLI behavior in query.py with mocked runtime dependencies.
# MODULE: Tests for the CLI entry point query.py
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from query import app

runner = CliRunner()

@pytest.fixture
def mock_health_status():
    """Provides a list of mocked health status objects."""
    status = MagicMock()
    status.name = "Ollama"
    status.ok = True
    status.detail = "Connected"
    return [status]

def test_cli_health(mock_health_status):
    """Verifies that the health command runs and prints a table."""
    with patch("query.collect_core_health", return_value=mock_health_status):
        result = runner.invoke(app, ["health"])
        assert result.exit_code == 0
        assert "Personal AI Brain Health" in result.stdout
        assert "Ollama" in result.stdout
        assert "ok" in result.stdout

def test_cli_route():
    """Verifies that the route command evaluates privacy rules."""
    result = runner.invoke(app, ["route", "religion"])
    assert result.exit_code == 0
    assert "Privacy Route Decision" in result.stdout
    assert "religion" in result.stdout
    assert "local" in result.stdout

def test_cli_count_mocked():
    """Verifies that the count command displays table statistics."""
    with patch("query.VectorStore") as mock_store_class:
        mock_instance = mock_store_class.return_value
        mock_instance.count.return_value = 42
        
        result = runner.invoke(app, ["count", "--table", "documents"])
        assert result.exit_code == 0
        assert "Vector Store Counts" in result.stdout
        assert "documents" in result.stdout
        assert "42" in result.stdout

def test_cli_search_validation():
    """Verifies that invalid search parameters are caught."""
    # Invalid table
    result = runner.invoke(app, ["search", "test", "--table", "invalid"])
    assert result.exit_code != 0
    assert "table must be one of" in result.stdout
    
    # Invalid top-k
    result = runner.invoke(app, ["search", "test", "--top-k", "0"])
    assert result.exit_code != 0
    assert "top-k must be >= 1" in result.stdout

def test_cli_search_empty_results():
    """Verifies search output when no results are found."""
    with patch("query._collect_results", return_value=[]):
        result = runner.invoke(app, ["search", "unknown query"])
        assert result.exit_code == 0
        assert "No results found" in result.stdout
