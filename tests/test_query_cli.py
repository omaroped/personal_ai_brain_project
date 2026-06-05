# MODULE: Tests for query.py command-line interface behavior using Typer's CLI runner.
"""Tests for the query.py CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from query import app

runner = CliRunner()


def test_health_command() -> None:
    """The health command should execute and return a success code."""
    result = runner.invoke(app, ["health"])
    assert result.exit_code == 0
    assert "Personal AI Brain Health" in result.stdout


def test_route_command_with_valid_domain() -> None:
    """The route command should resolve a domain and show details."""
    result = runner.invoke(app, ["route", "personal"])
    assert result.exit_code == 0
    assert "domain" in result.stdout
    assert "personal" in result.stdout
    assert "local" in result.stdout


def test_route_command_invalid_requested_route() -> None:
    """The route command should handle invalid route options gracefully."""
    result = runner.invoke(app, ["route", "ai_tech", "--requested-route", "invalid"])
    assert result.exit_code == 0
    assert "local" in result.stdout
    assert "Unsupported route" in result.stdout


def test_search_command_scaffold() -> None:
    """The search command should render the no-results path when mocked empty."""
    with patch("query._collect_results", return_value=[]):
        result = runner.invoke(app, ["search", "test query"])
    assert result.exit_code == 0
    assert "No results found." in result.stdout


def test_cli_argument_validation() -> None:
    """The CLI should fail when required arguments are missing."""
    result = runner.invoke(app, ["route"])  # Missing domain
    assert result.exit_code != 0
    assert "Missing argument" in result.stdout


def test_search_command_renders_results_table() -> None:
    """The search command should render results returned by the collection helper."""
    fake_result = MagicMock()
    fake_result.domain = "psychology"
    fake_result.page_number = 4
    fake_result.section = "Chapter 1"
    fake_result.score = 0.9
    fake_result.source_file = "psychology.pdf"
    fake_result.display_text = "[Source: psychology.pdf]\\nCognitive dissonance is discomfort."

    with patch("query._collect_results", return_value=[("documents", fake_result)]):
        result = runner.invoke(app, ["search", "cognitive dissonance"])

    assert result.exit_code == 0
    assert "Search Results: cognitive dissonance" in result.stdout
    assert "psychology.pdf" in result.stdout
