# Testing Guide: Personal AI Brain

## Overview
This project uses `pytest` for testing. Tests are designed to be fast, deterministic, and local-first.

## Test Categories

Tests are categorized by their environmental requirements. Use these categories to determine what can be run in constrained environments.

| Category | Requirements | Description | Example Files |
|---|---|---|---|
| **Offline** | None | Core logic, utilities, and unit tests. Fast and safe to run anywhere. | `test_foundation.py`, `test_chunker.py`, `test_privacy_router.py` |
| **Ollama-required** | Ollama API | Integration tests involving embeddings or LLM responses. | `test_embedder.py`, `test_phase1.py`, `test_query_cli.py` |
| **Docker-required** | Docker Compose | System-wide integration tests involving Letta or a full local service stack. | `test_phase2.py` |

## Running Tests

### 1. Basic Execution (Offline-safe)
To run the core logic tests that do not require external services:
```bash
source venv/bin/activate
pytest tests/test_foundation.py tests/test_parallel_foundations.py tests/test_privacy_router.py tests/test_ingestion_state.py tests/test_health_checks.py tests/test_logging_utils.py tests/test_watcher.py tests/test_file_types.py tests/test_text_normalization.py
```

### 2. Full Suite (Requires Services)
Some tests (like `test_phase1.py`) require local services to be running.

| Test File | Requires Ollama | Requires Letta | Requires Docker |
|---|---|---|---|
| `tests/test_embedder.py` | Sometimes | No | No |
| `tests/test_pipeline.py` | No | No | No |
| `tests/test_watcher.py` | No | No | No |
| `tests/test_phase1.py` | Yes | No | No |
| `tests/test_phase2.py` | Yes | Yes | Yes |

### 3. Service Readiness
Before running full-suite tests, verify your environment:
```bash
python scripts/verify_services.py
```

## Test Fixtures
- **Temporary Files:** Most tests use the `tmp_path` fixture to avoid touching real data.
- **Sample Files:** Located in `tests/fixtures/` for regression testing of extractors and chunkers.

## Writing New Tests
- Use `pytest.fixture` for reusable setup.
- Use `unittest.mock` for external dependencies (APIs, network).
- Follow the existing style in `tests/conftest.py`.
