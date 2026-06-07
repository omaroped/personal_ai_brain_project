# Observability

## Structured Logging

The project uses `src/common/logging_utils.py` as the canonical logging entrypoint.

- console output is human-readable
- file logs are structured JSON
- subsystems should call `configure_logging(__name__)`

## Current Observability Surfaces

- JSON file logs via rotating file handler
- planner execution traces
- voice IPC trace IDs
- `/control/status` control-plane snapshot
- health checks via `src/common/health.py`

## Gaps Still Open

- end-to-end trace propagation across every HTTP and voice request
- explicit p95 and resource metrics collection in CI
- restart/recovery observability for all services
