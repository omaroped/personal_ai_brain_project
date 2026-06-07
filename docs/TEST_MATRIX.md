# Test Matrix

## Purpose

This matrix defines which tests are safe in CI, which require local services, and which require audio or GPU hardware.

## Categories

### Pure unit tests

- no network
- no Ollama
- no Letta
- no audio devices
- CI-safe

Examples:

- `tests/test_foundation.py`
- `tests/test_chunker.py`
- `tests/test_text_normalization.py`
- `tests/test_phase6_runtime.py`

### Service-backed tests

- require Ollama and/or Letta
- may require Docker

Examples:

- `tests/test_phase1.py`
- `tests/test_phase2.py`
- `tests/test_query_cli.py`

### Audio or hardware-sensitive tests

- require local microphone/audio stack or GPU
- should run in local integration lanes, not default CI

Examples:

- `tests/test_phase4.py`
- voice benchmark scripts

## Recommended Commands

### CI-safe lane

```bash
python -m pytest tests/test_foundation.py tests/test_health_checks.py tests/test_logging_utils.py tests/test_text_normalization.py tests/test_planner.py tests/test_phase6_runtime.py
```

### Full local lane

```bash
python -m pytest tests/
```
