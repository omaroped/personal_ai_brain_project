# Agent Assignments

## Goal

Turn the sub-agent backlog into a concrete execution board.

## Agent A — Environment Bootstrap
- Status: COMPLETED. `requirements.txt` and `.env.example` added.

## Agent B — Core Config and Observability
- Status: COMPLETED. `config.py`, `logging_utils.py`, and `health.py` added.

## Agent C — Runtime and Service Wiring
- Status: COMPLETED. `docker/docker-compose.yml` added.

## Agent D — Developer Onboarding
- Status: COMPLETED. `README.md` and setup guides added.

## Agent E — Fixtures and Test Scaffold
- Status: COMPLETED. `tests/fixtures/`, `tests/test_foundation.py`, and `tests/conftest.py` added.

## Agent F — Ingestion State Foundation
- Status: COMPLETED. `src/ingestion/state.py` added.

## Immediate Follow-Up Assignments

### Agent G — Privacy Routing
- Status: COMPLETED. `src/api/privacy_router.py` added and verified.

### Agent H — CLI Skeleton
- Status: COMPLETED. `query.py` added with health and routing commands.

### Agent I — LanceDB Bootstrap
- Status: COMPLETED. `src/ingestion/vector_store.py` added with hybrid search helpers.

### Agent J — Benchmark Utilities
- Status: COMPLETED. `src/common/benchmarks.py` and initial tests added.

### Agent K — Architecture Documentation
- Status: COMPLETED. `plan/ARCHITECTURE.md` populated and reviewed.

### Agent L — Environment Repair Guidance
- Status: COMPLETED. `docs/ENVIRONMENT_FIX.md`, `scripts/rebuild_venv.sh`, and `scripts/smoke_test_ingestion.py` added.

### Agent M — Isolated Ingestion State Tests
- Status: COMPLETED. `tests/test_ingestion_state.py` and other focused logic tests added.

## Validation Blocker (RESOLVED / DOCUMENTED)

- The initial `venv/` was broken. 
- **Fix:** Documented in `docs/ENVIRONMENT_FIX.md`. A rebuild script `scripts/rebuild_venv.sh` is provided.
- **Note:** A TLS/SSL error was identified during automated rebuild; fix instructions (unsetting `SSL_CERT_FILE`) are included in the repair guide.
