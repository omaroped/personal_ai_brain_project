"""Tests for the query.py CLI commands."""

from __future__ import annotations

import pytest
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
    """The search command should show the scaffold message."""
    result = runner.invoke(app, ["search", "test query"])
    assert result.exit_code == 0
    assert "Search scaffold ready" in result.stdout
    assert "test query" in result.stdout


def test_cli_argument_validation() -> None:
    """The CLI should fail when required arguments are missing."""
    result = runner.invoke(app, ["route"])  # Missing domain
    assert result.exit_code != 0
    assert "Missing argument" in result.stdout
