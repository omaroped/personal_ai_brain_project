# Repo Map

## Top-Level Areas

- `src/api/` — FastAPI endpoints, dashboard transport, control plane
- `src/voice/` — daemon, VAD, STT, TTS, hotkey, protocol
- `src/ingestion/` — extraction, chunking, embeddings, vector store, web/youtube ingestion
- `src/memory/` — core memory, daily review, mistake tracking, provider adapters
- `src/agents/` — planner, sub-agent, state machine, tracing, tools
- `scripts/` — bootstrap, validation, smoke, benchmarks, runtime helpers
- `docs/` — architecture, operations, testing, Phase 6 hardening artifacts
- `tests/` — unit, phase acceptance, and runtime-hardening coverage

## High-Conflict Runtime Files

These files should be edited carefully in multi-agent sessions:

- `src/api/main.py`
- `src/voice/daemon.py`
- `src/voice/tts.py`
- `src/agents/tools/__init__.py`

## Recommended Read Order for New Contributors

1. `README.md`
2. `STATUS.md`
3. `docs/RUNTIME_TOPOLOGY.md`
4. `docs/SUBSYSTEM_BOUNDARIES.md`
5. `docs/TEST_MATRIX.md`
