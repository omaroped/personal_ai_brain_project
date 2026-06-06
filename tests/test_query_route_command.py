# MODULE: Tests for query.py 'route' command.
"""Tests for the route command in the query CLI."""

from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from query import app
from src.api.privacy_router import PrivacyDecision

runner = CliRunner()


def test_route_command_basic() -> None:
    """The route command should display the decision for a domain."""
    mock_decision = PrivacyDecision(
        domain="physics",
        route="local",
        allow_cloud=False,
        reason="Physics domain is marked as local-only."
    )
    with patch("query.choose_model_route", return_value=mock_decision):
        result = runner.invoke(app, ["route", "physics"])
    
    assert result.exit_code == 0
    assert "Privacy Route Decision" in result.stdout
    assert "domain" in result.stdout
    assert "physics" in result.stdout
    assert "route" in result.stdout
    assert "local" in result.stdout
    assert "reason" in result.stdout
    assert "Physics domain is marked as local-only." in result.stdout


def test_route_command_cloud_allowed() -> None:
    """The route command should show when cloud is allowed."""
    mock_decision = PrivacyDecision(
        domain="general",
        route="cloud",
        allow_cloud=True,
        reason="General domain allows cloud processing."
    )
    with patch("query.choose_model_route", return_value=mock_decision):
        result = runner.invoke(app, ["route", "general", "--requested-route", "cloud"])
    
    assert result.exit_code == 0
    assert "cloud" in result.stdout
    assert "True" in result.stdout


def test_route_command_missing_argument() -> None:
    """The route command should fail if domain is missing."""
    result = runner.invoke(app, ["route"])
    assert result.exit_code != 0
    assert "Missing argument" in (result.stdout or getattr(result, "stderr", ""))
