# MODULE: Central configuration for project paths, model names, privacy rules, and runtime settings.
"""Central configuration for the Personal AI Brain project."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _env_path(name: str, default: Path) -> Path:
    """Read a filesystem path from the environment or fall back to the default."""
    return Path(os.getenv(name, str(default))).expanduser()


def _env_path_list(name: str, defaults: list[Path]) -> list[Path]:
    """Read a colon-separated path list from the environment or use defaults."""
    raw = os.getenv(name, "")
    if not raw.strip():
        return defaults
    return [Path(item).expanduser() for item in raw.split(":") if item.strip()]

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = _env_path("BRAIN_DATA_DIR", PROJECT_ROOT / "data")
VAULT_DIR = _env_path("BRAIN_VAULT_DIR", DATA_DIR / "vault")
VECTORDB_DIR = _env_path("BRAIN_VECTORDB_DIR", DATA_DIR / "vectordb")
LOGS_DIR = _env_path("BRAIN_LOGS_DIR", DATA_DIR / "logs")
DOCKER_DIR = PROJECT_ROOT / "docker"
TESTS_DIR = PROJECT_ROOT / "tests"

WATCH_DIRS = _env_path_list(
    "BRAIN_WATCH_DIRS",
    [
        Path.home() / "Documents",
        Path.home() / "Downloads",
        VAULT_DIR,
    ],
)

INGESTION_INDEX_DB = _env_path("BRAIN_INGESTION_INDEX_DB", DATA_DIR / "ingestion_index.db")
LOG_FILE = _env_path("BRAIN_LOG_FILE", DATA_DIR / "logs" / "brain.log")
SETTINGS_FILE = _env_path("BRAIN_SETTINGS_FILE", DATA_DIR / "settings.json")

LANCEDB_DOCUMENTS = _env_path("BRAIN_LANCEDB_DOCUMENTS", VECTORDB_DIR / "documents")
LANCEDB_PERSONAL = _env_path("BRAIN_LANCEDB_PERSONAL", VECTORDB_DIR / "personal")
LANCEDB_CONVERSATIONS = _env_path("BRAIN_LANCEDB_CONVERSATIONS", VECTORDB_DIR / "conversations")
LANCEDB_ERRORS = _env_path("BRAIN_LANCEDB_ERRORS", VECTORDB_DIR / "errors")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LETTA_BASE_URL = os.getenv("LETTA_BASE_URL", "http://localhost:8283")
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8001"))

LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "mistral")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
CLOUD_LLM_MODEL = os.getenv("CLOUD_LLM_MODEL", "claude-sonnet-4-20250514")
EMBED_DIMENSIONS = 768

CHUNK_SIZE_DEFAULT = 512
CHUNK_OVERLAP_DEFAULT = 80
CHUNK_SIZE_RELIGIOUS = 256
CHUNK_OVERLAP_RELIGIOUS = 64
CHUNK_SIZE_LECTURE = 600
CHUNK_OVERLAP_LECTURE = 60

CLOUD_BLOCKED_DOMAINS = {"personal", "religion"}

LETTA_AGENT_NAME = "omar_brain"
OPENCLAW_BASE_URL = os.getenv("OPENCLAW_BASE_URL", "http://localhost:18789")
LETTA_SERVER_PASSWORD = os.getenv("LETTA_SERVER_PASSWORD", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

ENABLE_CLOUD_MODELS = os.getenv("ENABLE_CLOUD_MODELS", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def ensure_directories() -> None:
    """Create the core local directories required by the project."""
    for path in (
        DATA_DIR,
        VAULT_DIR,
        VECTORDB_DIR,
        LOGS_DIR,
        LANCEDB_DOCUMENTS,
        LANCEDB_PERSONAL,
        LANCEDB_CONVERSATIONS,
        LANCEDB_ERRORS,
    ):
        path.mkdir(parents=True, exist_ok=True)


def validate_environment() -> bool:
    """Check if critical external services (Ollama, Letta) are reachable."""
    import httpx
    
    services = {
        "Ollama": OLLAMA_BASE_URL,
        "Letta": LETTA_BASE_URL,
    }
    
    all_ok = True
    print("\n--- Environment Validation ---")
    for name, url in services.items():
        try:
            # Quick health ping
            endpoint = f"{url}/api/tags" if name == "Ollama" else f"{url}/health"
            resp = httpx.get(endpoint, timeout=2.0)
            if resp.status_code in (200, 404): # Letta might return 404 on /health if not configured
                print(f"  ✓ {name} is reachable.")
            else:
                print(f"  ✗ {name} returned status {resp.status_code}.")
                all_ok = False
        except Exception as exc:
            print(f"  ✗ {name} is OFFLINE ({exc}).")
            all_ok = False
    
    if not all_ok:
        print("\n  [!] Warning: Core services are missing. Run 'docker-compose up -d' first.\n")
    
    return all_ok


if __name__ == "__main__":
    ensure_directories()
    validate_environment()
    print("Configuration directories verified.")
