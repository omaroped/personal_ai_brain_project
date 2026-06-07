# Performance Budgets

## Purpose

These budgets define acceptable latency envelopes for the Personal AI Brain.
If a change exceeds these numbers without clear justification, treat it as a regression candidate.

## Budgets

| Path | Target | Notes |
|---|---:|---|
| Wake-word reaction | `< 150ms` | Detection and activation path only |
| STT first transcript result | `< 600ms` | For short local utterances on target hardware |
| Retrieval latency | `< 250ms` | Local hybrid search excluding LLM reasoning |
| Planner first tool decision | `< 1200ms` | Local-only baseline |
| TTS first audio chunk | `< 250ms` | After text is available |
| Full voice roundtrip | `< 1500ms` | Existing Phase 4 target |

## Measurement Sources

- `scripts/benchmark_voice.py`
- `scripts/benchmark_runtime.py`
- planner execution traces
- voice IPC trace IDs
