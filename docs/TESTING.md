# Testing Guide: Personal AI Brain

## Overview
This project uses `pytest` for testing. Tests are designed to be fast, deterministic, and local-first.

## Running Tests

### 1. Basic Execution (Offline-safe)
To run the core logic tests that do not require external services:
```bash
source venv/bin/activate
pytest tests/test_foundation.py tests/test_parallel_foundations.py tests/test_privacy_router.py tests/test_ingestion_state.py tests/test_health_checks.py tests/test_logging_utils.py
```

### 2. Full Suite (Requires Services)
Some tests (like `test_phase1.py`) require local services to be running.

| Test File | Requires Ollama | Requires Letta | Requires Docker |
|---|---|---|---|
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
