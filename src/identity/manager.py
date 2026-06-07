# MODULE: Unified identity manager for provider selection, fallback, and memory sync.
"""Canonical identity subsystem entrypoint."""

from __future__ import annotations

from dataclasses import dataclass
import json

import config
from src.common.logging_utils import configure_logging
from src.memory.letta_agent import OmarBrainAgent
from src.memory.openclaw_agent import OpenClawAgent

LOGGER = configure_logging(__name__)


@dataclass
class IdentityResponse:
    """Normalized response from the identity layer."""

    text: str
    provider: str
    used_fallback: bool = False


class IdentityManager:
    """Owns provider selection, conversational fallback, and memory sync hooks."""

    def __init__(
        self,
        letta_agent: OmarBrainAgent | None = None,
        openclaw_agent: OpenClawAgent | None = None,
    ) -> None:
        self.letta_agent = letta_agent or OmarBrainAgent()
        self.openclaw_agent = openclaw_agent or OpenClawAgent()

    def respond(self, message: str, context: dict | None = None) -> IdentityResponse:
        """Route a conversational input to the best available provider."""
        context = context or {}
        turbo_mode, openclaw_mode = self._read_runtime_modes()

        if openclaw_mode:
            response = self.openclaw_agent.send_message(message)
            if not self._looks_like_provider_error(response):
                return IdentityResponse(text=response, provider="openclaw", used_fallback=False)
            LOGGER.warning("OpenClaw path failed; falling back to next provider.")

        if turbo_mode and config.GEMINI_API_KEY:
            try:
                import google.generativeai as genai

                genai.configure(api_key=config.GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash")
                return IdentityResponse(
                    text=model.generate_content(message).text,
                    provider="gemini",
                    used_fallback=openclaw_mode,
                )
            except Exception as exc:
                LOGGER.error("Gemini provider failed: %s", exc)

        return IdentityResponse(
            text=self.letta_agent.send_message(message),
            provider="letta",
            used_fallback=openclaw_mode or turbo_mode,
        )

    def health(self) -> dict:
        """Return lightweight identity-provider readiness information."""
        return {
            "letta_ready": bool(self.letta_agent.agent_id),
            "openclaw_available": True,
            "gemini_configured": bool(config.GEMINI_API_KEY),
        }

    def warmup(self) -> None:
        """Prepare the default identity backend."""
        self.letta_agent.ensure_agent()

    def sync_memory(self) -> None:
        """Hook for future full identity-memory synchronization."""
        try:
            self.letta_agent.ensure_agent()
        except Exception as exc:
            LOGGER.warning("Identity memory sync warmup failed: %s", exc)

    def _read_runtime_modes(self) -> tuple[bool, bool]:
        turbo_mode = False
        openclaw_mode = True
        if config.SETTINGS_FILE.exists():
            try:
                with open(config.SETTINGS_FILE, "r", encoding="utf-8") as handle:
                    settings = json.load(handle)
                turbo_mode = settings.get("turbo", False)
                openclaw_mode = settings.get("openclaw", True)
            except Exception as exc:
                LOGGER.warning("Failed to read runtime settings: %s", exc)
        return turbo_mode, openclaw_mode

    def _looks_like_provider_error(self, response: str) -> bool:
        lowered = response.lower()
        return "error:" in lowered or "trouble connecting" in lowered or "timed out" in lowered
