# MODULE: Structured core memory persistence with Letta health checks and sync support.
"""Core memory management and lightweight Letta runtime integration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import tempfile

import httpx

from config import LETTA_AGENT_NAME, LETTA_BASE_URL, LOCAL_LLM_MODEL, EMBED_MODEL
from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)

DEFAULT_CORE_MEMORY_SCHEMA = {
    "identity": {},
    "domains": [],
    "goals": [],
    "mistakes": [],
    "preferences": {},
    "active_projects": [],
    "last_reviewed_at": "",
}


class LettaUnavailableError(RuntimeError):
    """Raised when Letta cannot be reached or refuses the request."""


@dataclass
class LettaRuntime:
    """Small HTTP wrapper for Letta health checks and agent creation."""

    base_url: str = LETTA_BASE_URL
    agent_name: str = LETTA_AGENT_NAME
    timeout: float = 5.0

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            response = httpx.request(method, url, timeout=self.timeout, follow_redirects=True, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as exc:
            raise LettaUnavailableError(f"Letta request failed for {url}: {exc}") from exc

    def assert_healthy(self) -> None:
        """Fail fast if Letta is unavailable."""
        try:
            self._request("GET", "/v1/health/")
        except Exception:
            self._request("GET", "/health")

    def ensure_agent(self) -> dict:
        """Return the configured agent if it exists, otherwise create it."""
        self.assert_healthy()

        list_candidates = ["/v1/agents", "/agents"]
        for path in list_candidates:
            try:
                response = self._request("GET", path)
                payload = response.json()
                agents = payload.get("agents", payload) if isinstance(payload, dict) else payload
                if isinstance(agents, list):
                    for agent in agents:
                        if agent.get("name") == self.agent_name:
                            return agent
                    break
            except LettaUnavailableError:
                continue
            except (ValueError, AttributeError, TypeError):
                continue

        model_handle = f"ollama/{LOCAL_LLM_MODEL}" if not LOCAL_LLM_MODEL.startswith("ollama/") else LOCAL_LLM_MODEL
        embed_handle = f"ollama/{EMBED_MODEL}" if not EMBED_MODEL.startswith("ollama/") else EMBED_MODEL

        create_payload = {
            "name": self.agent_name,
            "memory": "Core identity synced from local structured memory.",
            "model": model_handle,
            "embedding": embed_handle,
        }
        create_candidates = ["/v1/agents", "/agents"]
        last_error: Exception | None = None
        for path in create_candidates:
            try:
                response = self._request("POST", path, json=create_payload)
                return response.json() if response.content else create_payload
            except LettaUnavailableError as exc:
                last_error = exc
                continue
            except ValueError:
                return create_payload

        if last_error is not None:
            raise last_error
        raise LettaUnavailableError("Unable to create or discover Letta agent")

    def sync_memory_summary(self, summary: str) -> None:
        """Push a concise memory summary to Letta if an update endpoint exists."""
        agent = self.ensure_agent()
        agent_id = agent.get("id") or agent.get("agent_id") or self.agent_name
        payload = {"memory": summary}

        candidates = [
            f"/v1/agents/{agent_id}/memory",
            f"/agents/{agent_id}/memory",
            f"/v1/agents/{agent_id}",
            f"/agents/{agent_id}",
        ]
        last_error: Exception | None = None
        for path in candidates:
            for method in ("PATCH", "POST", "PUT"):
                try:
                    self._request(method, path, json=payload)
                    return
                except LettaUnavailableError as exc:
                    last_error = exc
                    continue
        if last_error is not None:
            raise last_error
        raise LettaUnavailableError("Unable to sync memory summary to Letta")


def _atomic_write_json(path: Path, payload: dict) -> None:
    """Persist JSON atomically to avoid partial file corruption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    ) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


@dataclass
class CoreMemoryManager:
    """Manage a local core memory JSON file and Letta synchronization."""

    memory_path: Path
    letta_runtime: LettaRuntime | None = None

    def load(self) -> dict:
        """Load core memory, creating or repairing it when needed."""
        if not self.memory_path.exists():
            return self.ensure_schema()

        try:
            payload = json.loads(self.memory_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            backup_path = self.memory_path.with_suffix(f"{self.memory_path.suffix}.bak")
            backup_path.write_text(self.memory_path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
            LOGGER.error("Invalid core memory JSON detected; backed up to %s", backup_path)
            return self.ensure_schema()

        if not isinstance(payload, dict):
            LOGGER.error("Core memory payload was not an object; resetting schema")
            return self.ensure_schema()

        return self._merge_with_schema(payload)

    def save(self, payload: dict) -> None:
        """Persist a payload while preserving required schema keys."""
        merged = self._merge_with_schema(payload)
        _atomic_write_json(self.memory_path, merged)

    def ensure_schema(self) -> dict:
        """Ensure the memory file exists with all required schema keys."""
        payload = self._merge_with_schema({})
        self.save(payload)
        return payload

    def update_section(self, section: str, value: dict | list | str) -> None:
        """Update one top-level section without dropping unrelated keys."""
        payload = self.load()
        payload[section] = value
        self.save(payload)

    def sync_to_letta(self) -> None:
        """Push a concise summary of the current memory state to Letta."""
        runtime = self.letta_runtime or LettaRuntime()
        payload = self.load()
        summary_parts = [
            f"identity={json.dumps(payload.get('identity', {}), ensure_ascii=True, sort_keys=True)}",
            f"domains={', '.join(payload.get('domains', [])) or 'none'}",
            f"goals={'; '.join(payload.get('goals', [])) or 'none'}",
            f"active_projects={'; '.join(payload.get('active_projects', [])) or 'none'}",
            f"last_reviewed_at={payload.get('last_reviewed_at', '') or 'unknown'}",
        ]
        summary = " | ".join(summary_parts)
        runtime.sync_memory_summary(summary)

    def _merge_with_schema(self, payload: dict) -> dict:
        merged = dict(payload)
        for key, default_value in DEFAULT_CORE_MEMORY_SCHEMA.items():
            if key not in merged:
                merged[key] = default_value.copy() if isinstance(default_value, dict) else list(default_value) if isinstance(default_value, list) else default_value
        return merged
