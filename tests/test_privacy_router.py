# MODULE: Tests for privacy routing decisions and domain normalization behavior.
"""Tests for the privacy routing logic."""

from __future__ import annotations

import pytest

from src.api.privacy_router import (
    choose_model_route,
    is_cloud_allowed_for_domain,
    normalize_domain,
)


def test_normalize_domain() -> None:
    """Domain strings should be lowercased and stripped."""
    assert normalize_domain("  Psychology  ") == "psychology"
    assert normalize_domain(None) == "unknown"
    assert normalize_domain("") == "unknown"


def test_cloud_allowance_for_sensitive_domains() -> None:
    """Sensitive domains and disabled cloud mode must keep routing local."""
    assert is_cloud_allowed_for_domain("personal") is False
    assert is_cloud_allowed_for_domain("religion") is False
    assert is_cloud_allowed_for_domain("anything_else") is False


def test_route_selection_auto() -> None:
    """Auto routing should respect privacy rules."""
    # Sensitive -> local
    decision = choose_model_route("personal")
    assert decision.route == "local"
    assert decision.allow_cloud is False
    
    # Non-sensitive -> local (default for now)
    decision = choose_model_route("ai_tech")
    assert decision.route == "local"


def test_route_selection_explicit_local() -> None:
    """Explicit local requests should always stay local."""
    decision = choose_model_route("ai_tech", requested_route="local")
    assert decision.route == "local"


def test_route_selection_explicit_cloud_blocked() -> None:
    """Explicit cloud requests for blocked domains should be downgraded to local."""
    decision = choose_model_route("religion", requested_route="cloud")
    assert decision.route == "local"
    assert decision.allow_cloud is False
    assert "blocked by privacy policy" in decision.reason


def test_route_selection_invalid_option() -> None:
    """Invalid route options should fall back to local safely."""
    decision = choose_model_route("ai_tech", requested_route="sideways")
    assert decision.route == "local"
    assert "Unsupported route" in decision.reason
