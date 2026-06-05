# STATUS.md — Project State Tracker
# The agent reads this file at the start of EVERY session.
# The agent updates this file after EVERY completed task.

---

## Current State

**Phase:** 1 — The Vault
**Active Spec:** `specs/phase1_vault.md`
**Last Updated:** 2026-06-06
**Overall Progress:** 70%

---

## Phase 1 Tasks

- [ ] **Task 1.0** — Bootstrap: create venv, install requirements, verify Ollama + Docker
- [ ] **Task 1.1** — Write `config.py` (all paths and constants)
- [ ] **Task 1.2** — Write `src/ingestion/watcher.py` (file watcher with debounce)
- [ ] **Task 1.3** — Write `src/ingestion/pdf_extractor.py` (pymupdf + scanned PDF detection)
- [ ] **Task 1.4** — Write `src/ingestion/chunker.py` (structural + recursive hybrid strategy)
- [ ] **Task 1.5** — Write `src/ingestion/embedder.py` (nomic-embed-text via Ollama + domain tagger)
- [ ] **Task 1.6** — Write `src/ingestion/vector_store.py` (LanceDB setup, hybrid search)
- [ ] **Task 1.7** — Wire everything: `src/ingestion/pipeline.py` (watcher → extractor → chunker → embedder → store)
- [ ] **Task 1.8** — Write `tests/test_phase1.py` and pass all 5 acceptance tests
- [ ] **Task 1.9** — Write `query.py` CLI (search the vault from terminal)

---

## Phase 2 Tasks (do not start until Phase 1 is 100% complete)

- [ ] **Task 2.1** — Configure Letta with Ollama backend, create `omar_brain` agent
- [ ] **Task 2.2** — Write `src/memory/core_memory.py` (load/update core_memory.json)
- [ ] **Task 2.3** — Write `src/memory/daily_review.py` (nightly review script + systemd timer)
- [ ] **Task 2.4** — Write `src/memory/extractor.py` (parse daily log → update core memory)
- [ ] **Task 2.5** — Write `src/memory/mistake_tracker.py` (error log + pre-task check)
- [ ] **Task 2.6** — Write `tests/test_phase2.py` and pass all acceptance tests

---

## Phase 3 Tasks (do not start until Phase 2 is 100% complete)

- [ ] **Task 3.1** — Write `src/ingestion/web_endpoint.py` (FastAPI /ingest/web)
- [ ] **Task 3.2** — Write bookmarklet snippet + instructions
- [ ] **Task 3.3** — Write `src/ingestion/youtube_ingestor.py` (yt-dlp transcript pipeline)
- [ ] **Task 3.4** — Write `src/ingestion/auto_tagger.py` (domain + content type classifier)
- [ ] **Task 3.5** — Write `tests/test_phase3.py` and pass all acceptance tests

---

## Phase 4 Tasks (do not start until Phase 3 is 100% complete)

- [ ] **Task 4.1** — Install + benchmark faster-whisper on CUDA (target: <200ms for 5s clip)
- [ ] **Task 4.2** — Write `src/voice/vad.py` (Silero VAD recording loop)
- [ ] **Task 4.3** — Write `src/voice/stt.py` (faster-whisper transcription service)
- [ ] **Task 4.4** — Write `src/voice/tts.py` (Kokoro ONNX streaming playback)
- [ ] **Task 4.5** — Write `src/voice/pipeline.py` (full VAD → STT → Brain → TTS loop)
- [ ] **Task 4.6** — Add hotkey trigger (Ctrl+Space via pynput)
- [ ] **Task 4.7** — Write `tests/test_phase4.py` (latency benchmark: must be <1.5s end-to-end)

---

## Phase 5 Tasks (do not start until Phase 4 is 100% complete)

- [ ] **Task 5.1** — Write `src/agents/planner.py` (goal → task breakdown)
- [ ] **Task 5.2** — Write `src/agents/sub_agent.py` (isolated context window executor)
- [ ] **Task 5.3** — Configure Bytebot Docker sandbox
- [ ] **Task 5.4** — Write `src/agents/proactive.py` (window title monitor + notification)
- [ ] **Task 5.5** — Write `tests/test_phase5.py`

---

## Blocked Tasks

- **Task 1.0 / Runtime Validation** — The checked-in `venv/` points to an inaccessible Python 3.11 runtime, and the system `python3` in this shell does not provide `venv`, `pip`, or `pytest`. Code implementation is far along, but end-to-end validation is blocked until a working Python environment is restored.

---

## Next Session Should Start With

```
Read CLAUDE.md and STATUS.md.
Tell me what phase we are in and what the first uncompleted task is.
Wait for my confirmation before writing any code.
```

---

## Session Log

| Date | Tasks completed | Notes |
|------|----------------|-------|
| 2026-06-06 | Phase 1 implementation in progress | Core ingestion modules, CLI, and supporting tests/docs were added; runtime validation remains blocked by the Python environment. |
| 2026-06-06 | Documentation and Missing Scripts | Created scripts/run_unit_subset.sh and 5 key documentation files (ENVIRONMENT_MATRIX.md, INGESTION_FLOW.md, PRIVACY_MODEL.md, VECTOR_STORE_NOTES.md, WATCHER_BEHAVIOR.md). |
