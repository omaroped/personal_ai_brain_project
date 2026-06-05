# MODULE: Privacy routing helpers that enforce local-only handling for sensitive domains.
"""Privacy routing utilities for deciding whether content may use cloud models."""

from __future__ import annotations

from dataclasses import dataclass

from config import CLOUD_BLOCKED_DOMAINS, ENABLE_CLOUD_MODELS


@dataclass(frozen=True)
class PrivacyDecision:
    """Represents a routing decision for model usage.

    Parameters:
        domain: Content domain being evaluated.
        allow_cloud: Whether cloud model access is allowed.
        route: Resolved execution route, either local or cloud.
        reason: Human-readable explanation for the routing decision.
    """

    domain: str
    allow_cloud: bool
    route: str
    reason: str


def normalize_domain(domain: str | None) -> str:
    """Normalize a possibly empty domain value into a stable lowercase label.

    Parameters:
        domain: Raw domain label, possibly None.

    Returns:
        str: Normalized domain label.
    """
    if domain is None:
        return "unknown"
    normalized = domain.strip().lower()
    return normalized or "unknown"


def is_cloud_allowed_for_domain(domain: str | None) -> bool:
    """Determine whether a domain is eligible for cloud model use.

    Parameters:
        domain: Raw content domain.

    Returns:
        bool: True when cloud use is permitted, otherwise False.
    """
    normalized_domain = normalize_domain(domain)
    if not ENABLE_CLOUD_MODELS:
        return False
    return normalized_domain not in CLOUD_BLOCKED_DOMAINS


def choose_model_route(domain: str | None, requested_route: str = "auto") -> PrivacyDecision:
    """Resolve a safe execution route for a piece of content.

    Parameters:
        domain: Content domain being processed.
        requested_route: Caller preference: `auto`, `local`, or `cloud`.

    Returns:
        PrivacyDecision: Resolved route and explanation.
    """
    normalized_domain = normalize_domain(domain)
    normalized_request = requested_route.strip().lower()

    if normalized_request not in {"auto", "local", "cloud"}:
        return PrivacyDecision(
            domain=normalized_domain,
            allow_cloud=False,
            route="local",
            reason=f"Unsupported route '{requested_route}', defaulting to local.",
        )

    if normalized_request == "local":
        return PrivacyDecision(
            domain=normalized_domain,
            allow_cloud=False,
            route="local",
            reason="Caller explicitly requested local execution.",
        )

    cloud_allowed = is_cloud_allowed_for_domain(normalized_domain)
    if normalized_request == "cloud":
        if cloud_allowed:
            return PrivacyDecision(
                domain=normalized_domain,
                allow_cloud=True,
                route="cloud",
                reason="Caller requested cloud execution and the domain is allowed.",
            )
        return PrivacyDecision(
            domain=normalized_domain,
            allow_cloud=False,
            route="local",
            reason="Cloud execution was requested but blocked by privacy policy.",
        )

    if cloud_allowed:
        return PrivacyDecision(
            domain=normalized_domain,
            allow_cloud=True,
            route="cloud",
            reason="Automatic routing selected cloud because the domain is allowed.",
        )

    return PrivacyDecision(
        domain=normalized_domain,
        allow_cloud=False,
        route="local",
        reason="Automatic routing selected local due to privacy policy or disabled cloud mode.",
    )
