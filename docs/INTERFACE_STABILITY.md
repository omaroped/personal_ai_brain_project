# Interface Stability

## Stable Public Interfaces

- FastAPI endpoints under `src/api/main.py`
- ingestion entrypoints under `src/ingestion/`
- memory manager interfaces in `src/memory/`
- voice IPC protocol in `src/voice/protocol.py`

## Semi-Stable Internal Interfaces

- planner invocation through `TaskPlanner.execute()`
- control-plane snapshot format
- tool registry contracts in `src/agents/tools/`

## Experimental Interfaces

- provider-selection behavior
- sandbox/browser tools
- screen capture and vision tooling
- cloud bridge integrations

## Guidance

Contributors should prefer extending stable interfaces before depending on internal implementation details.
