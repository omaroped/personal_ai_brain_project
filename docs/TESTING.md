# Testing Guide: Personal AI Brain

## Overview
This project uses `pytest` for unit and integration testing. Tests are designed to be isolated, deterministic, and safe to run in restricted environments.

## Running Tests

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Run All Tests
```bash
pytest -v
```

### 3. Run a Specific Phase/File
```bash
pytest tests/test_phase1.py -v
```

## Testing Without External Services
Many tests are designed to run without **Ollama**, **Letta**, or **Docker** by using mocks and temporary directories.

- **Offline-Safe Tests:**
  - `tests/test_foundation.py`
  - `tests/test_ingestion_state.py`
  - `tests/test_privacy_router.py`
  - `tests/test_cli_foundation.py`
- **Service-Dependent Tests:**
  - `tests/test_phase1.py` (requires Ollama for embeddings)
  - `tests/test_parallel_foundations.py` (requires Ollama)

## Fixture Policy
- **Fixtures Directory:** `tests/fixtures/` contains sample files (.pdf, .md, .txt, .docx).
- **Temporary Data:** Always use the `temp_data_dir` or `temp_db_path` fixtures from `tests/conftest.py` to avoid touching real project data.
- **Mocking:** Prefer mocking `Embedder.embed()` and `requests` to ensure tests remain fast and deterministic.

## Rebuilding the Environment
If you encounter shared library errors (e.g., `libpython3.11.so.1.0`), run the rebuild script:
```bash
bash scripts/rebuild_venv.sh
```
See `docs/ENVIRONMENT_FIX.md` for more details.

## Continuous Validation
A task is not considered **Complete** until all relevant tests pass with `pytest`.
