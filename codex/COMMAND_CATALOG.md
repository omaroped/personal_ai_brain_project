# Command Catalog

This document lists useful scripts and commands for development, testing, and operations.

## Core CLI Tools

| Command | Description |
|---|---|
| `python query.py` | Search the vault and query the brain from the terminal. |

## Development Scripts (scripts/)

| Command | Description |
|---|---|
| `python scripts/list_project_modules.py` | Enumerate all project-owned Python modules. |
| `python scripts/check_module_headers.py` | Enforce `# MODULE:` headers in Python files. |
| `python scripts/check_docstrings.py` | Enforce function and class docstrings. |
| `python scripts/print_python_env.py` | Print details about the current Python environment. |
| `python scripts/verify_services.py` | Check readiness of Ollama, Docker, and other services. |
| `./scripts/rebuild_venv.sh` | Rebuild the local virtual environment. |
| `python scripts/benchmark_stub.py` | Placeholder for latency and throughput benchmarks. |

## Testing Commands

| Command | Description |
|---|---|
| `pytest` | Run the full test suite. |
| `pytest tests/test_phase1.py` | Run Phase 1 specific tests. |
