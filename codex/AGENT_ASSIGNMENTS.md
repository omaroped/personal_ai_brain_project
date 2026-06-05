# Agent Assignments

## Goal

Turn the sub-agent backlog into a concrete execution board.

## Agent A — Environment Bootstrap

Files:
- `requirements.txt`
- `.env.example`

Done when:
- dependencies are grouped clearly
- environment variables are documented

Risk:
- low

Status:
- `requirements.txt` present
- `.env.example` added

## Agent B — Core Config and Observability

Files:
- `config.py`
- `src/common/logging_utils.py`
- `src/common/health.py`

Done when:
- core paths and service URLs are centralized
- logging can be configured consistently
- health checks run without app-specific code

Risk:
- low

Status:
- core foundation added

## Agent C — Runtime and Service Wiring

Files:
- `docker/docker-compose.yml`

Done when:
- Letta can be started with one compose command
- persistence is configured
- health checks are defined

Risk:
- medium

Status:
- compose file added

## Agent D — Developer Onboarding

Files:
- `README.md`

Done when:
- a new session can bootstrap the project from the README
- setup and verification commands are documented

Risk:
- low

Status:
- README added

## Agent E — Fixtures and Test Scaffold

Files:
- `tests/fixtures/`
- `tests/test_foundation.py`

Done when:
- baseline fixtures exist
- shared foundation is covered by tests

Risk:
- low

Status:
- fixtures and baseline tests added
- `tests/conftest.py` added

## Agent F — Ingestion State Foundation

Files:
- `src/ingestion/state.py`

Done when:
- duplicate detection helpers exist
- SQLite ingestion index schema exists
- file hash utilities are reusable

Risk:
- low

Status:
- initial implementation added

## Immediate Follow-Up Assignments

### Agent G — Privacy Routing

Files:
- `src/api/privacy_router.py`

Done when:
- local-only enforcement exists for sensitive domains

Risk:
- low

Status:
- privacy routing foundation added

### Agent H — CLI Skeleton

Files:
- `query.py`
- or future `src/cli/`

Done when:
- one stable operational command surface exists

Risk:
- low

Status:
- CLI scaffold added with health and routing commands

### Agent I — LanceDB Bootstrap

Files:
- `src/ingestion/vector_store.py`

Done when:
- schemas and bootstrap logic exist without full retrieval integration yet

Risk:
- medium

Status:
- vector store implementation now exceeds bootstrap scope and includes search helpers

### Agent J — Benchmark Utilities

Files:
- `src/common/benchmarks.py`
- `tests/test_parallel_foundations.py`

Done when:
- timing helpers exist for ingestion, retrieval, and voice latency measurement
- benchmark utilities are covered by focused tests

Risk:
- low

Status:
- benchmark utility foundation added

### Agent K — Architecture Documentation

Files:
- `plan/ARCHITECTURE.md`

Done when:
- the previously empty architecture document is populated with current component and data-flow structure

Risk:
- low

Status:
- architecture document added by supporting agent

### Agent L — Environment Repair Guidance

Files:
- `docs/ENVIRONMENT_FIX.md`
- `scripts/rebuild_venv.sh`

Done when:
- the current virtualenv failure mode is documented
- a rebuild path exists without changing lead-owned runtime files

Risk:
- low

Status:
- environment repair note and rebuild script added

### Agent M — Isolated Ingestion State Tests

Files:
- `tests/test_ingestion_state.py`

Done when:
- hashing and SQLite ingestion-state behavior are covered outside the lead-owned Phase 1 test file

Risk:
- low

Status:
- isolated ingestion-state tests added

## Validation Blocker

- The checked-in `venv/` expects Python 3.11 shared libraries that are not available in this shell.
- Result: `venv/bin/python` and `venv/bin/pytest` are not usable here.
- Additional blocker: system `python3` does not provide `venv`, `pip`, or `pytest`, so a non-destructive local fallback environment could not be created from this shell.
- Impact: syntax verification passed with system `python3`, but full pytest execution still depends on repairing or recreating a working Python environment.
