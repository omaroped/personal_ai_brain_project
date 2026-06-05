# Environment Matrix

This document compares the various Python environments encountered during development and specifies the intended runtime for the Personal AI Brain project.

| Component | Broken venv (checked-in) | System python3 | Intended Runtime (Fixed) |
|-----------|--------------------------|----------------|--------------------------|
| Python Version | 3.11 (hardcoded runner paths) | 3.10.x | 3.11+ |
| `venv` module | Present (broken links) | Missing | Present |
| `pip` | Present (broken links) | Missing | Present |
| `pytest` | Present (broken links) | Missing | Present |
| Ollama | External | External | Reachable (local or network) |
| Docker | External | External | Reachable (local or network) |
| Path consistency | Fails (points to /home/runner) | Works (local) | Works (local) |

## Context
The project was initialized with a pre-configured `venv/` directory that contained hardcoded absolute paths pointing to a GitHub Actions runner environment (`/home/runner/...`). This rendered the environment unusable on local machines. The system Python on the target environment often lacks the necessary modules to rebuild the virtual environment directly without manual intervention (e.g., `apt-get install python3-venv`).
