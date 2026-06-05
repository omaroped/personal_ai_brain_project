# MODULE: Central configuration for project paths, model names, privacy rules, and runtime settings.
"""Central configuration for the Personal AI Brain project."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
VAULT_DIR = DATA_DIR / "vault"
VECTORDB_DIR = DATA_DIR / "vectordb"
LOGS_DIR = DATA_DIR / "logs"
DOCKER_DIR = PROJECT_ROOT / "docker"
TESTS_DIR = PROJECT_ROOT / "tests"

WATCH_DIRS = [
    Path("/home/omar/Documents"),
    Path("/home/omar/Downloads"),
    VAULT_DIR,
]

INGESTION_INDEX_DB = DATA_DIR / "ingestion_index.db"
LOG_FILE = DATA_DIR / "logs" / "brain.log"

LANCEDB_DOCUMENTS = VECTORDB_DIR / "documents"
LANCEDB_PERSONAL = VECTORDB_DIR / "personal"
LANCEDB_CONVERSATIONS = VECTORDB_DIR / "conversations"
LANCEDB_ERRORS = VECTORDB_DIR / "errors"

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
LETTA_SERVER_PASSWORD = os.getenv("LETTA_SERVER_PASSWORD", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

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


if __name__ == "__main__":
    ensure_directories()
    print("Configuration directories verified.")
