# MODULE: OpenClaw bridge for using existing authenticated sessions.
"""Bridge to the local OpenClaw CLI for high-speed, authenticated reasoning."""

from __future__ import annotations

import subprocess
import logging
from typing import Any, Dict

from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)

class OpenClawAgent:
    """Uses the local OpenClaw CLI to route messages to Codex/Gemini without API keys."""

    def __init__(self, model_id: str = "openai-codex/gpt-5.5") -> None:
        self.model_id = model_id

    def send_message(self, text: str) -> str:
        """
        Route message through OpenClaw CLI.
        
        Parameters:
            text: User input.
            
        Returns:
            str: Assistant response.
        """
        LOGGER.info("Routing message through OpenClaw CLI: '%s'", text[:50])
        
        try:
            # We don't need an API Key because OpenClaw handles auth locally
            # We use the raw output to avoid parsing the CLI headers
            prompt = f"System: You are Omar's AI Brain. Be concise.\nUser: {text}"
            
            result = subprocess.run(
                ["openclaw", "infer", "model", "run", "--model", self.model_id, "--prompt", prompt],
                capture_output=True,
                text=True,
                timeout=60.0
            )
            
            if result.returncode != 0:
                LOGGER.error("OpenClaw CLI failed: %s", result.stderr)
                return "Error: OpenClaw execution failed."
            
            # OpenClaw CLI outputs some headers before the actual text
            # E.g.
            # │
            # ◇  
            # OpenClaw 2026.5.27...
            # outputs: 1
            # <Actual response>
            
            lines = result.stdout.strip().split("\n")
            
            # Find the line that says 'outputs: 1' and take everything after it
            response_start = 0
            for i, line in enumerate(lines):
                if line.startswith("outputs: 1"):
                    response_start = i + 1
                    break
            
            if response_start > 0:
                return "\n".join(lines[response_start:]).strip()
            
            # Fallback if parsing fails
            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            return "Error: OpenClaw CLI timed out."
        except Exception as exc:
            LOGGER.error("OpenClaw bridge failed: %s", exc)
            return f"I had trouble connecting to my cloud gateway (OpenClaw). Is it installed in PATH? {exc}"

if __name__ == "__main__":
    # Quick test
    bridge = OpenClawAgent()
    print(bridge.send_message("Hello, who are you?"))
