# STATUS.md — Project State Tracker
# The agent reads this file at the start of EVERY session.
# The agent updates this file after EVERY completed task.

---

## Current State

**Phase:** 3 — Ingestion Pipelines (complete, moving to Phase 4)
**Active Spec:** `specs/phase4_voice.md`
**Last Updated:** 2026-06-06
**Overall Progress:** 100% (Phase 3 complete)

---

## Phase 1 Tasks

- [x] **Task 1.0** — Bootstrap: create venv, install requirements, verify Ollama + Docker
- [x] **Task 1.1** — Write `config.py` (all paths and constants)
- [x] **Task 1.2** — Write `src/ingestion/watcher.py` (file watcher with debounce)
- [x] **Task 1.3** — Write `src/ingestion/pdf_extractor.py` (pymupdf + scanned PDF detection)
- [x] **Task 1.4** — Write `src/ingestion/chunker.py` (structural + recursive hybrid strategy)
- [x] **Task 1.5** — Write `src/ingestion/embedder.py` (nomic-embed-text via Ollama + domain tagger)
- [x] **Task 1.6** — Write `src/ingestion/vector_store.py` (LanceDB setup, hybrid search)
- [x] **Task 1.7** — Wire everything: `src/ingestion/pipeline.py` (watcher → extractor → chunker → embedder → store)
- [x] **Task 1.8** — Write `tests/test_phase1.py` and pass all 5 acceptance tests
- [x] **Task 1.9** — Write `query.py` CLI (search the vault from terminal)

---

## Phase 2 Tasks

- [x] **Task 2.1** — Configure Letta with Ollama backend, create `omar_brain` agent
- [x] **Task 2.2** — Write `src/memory/core_memory.py` (load/update core_memory.json)
- [x] **Task 2.3** — Write `src/memory/daily_review.py` (nightly review script + systemd timer)
- [x] **Task 2.4** — Write `src/memory/extractor.py` (parse daily log → update core memory)
- [x] **Task 2.5** — Write `src/memory/mistake_tracker.py` (error log + pre-task check)
- [x] **Task 2.6** — Write `tests/test_phase2.py` and pass all acceptance tests

---

## Phase 3 Tasks (do not start until Phase 2 is 100% complete)

- [x] **Task 3.1** — Write `src/ingestion/web_endpoint.py` (FastAPI /ingest/web)
- [x] **Task 3.2** — Write bookmarklet snippet + instructions
- [x] **Task 3.3** — Write `src/ingestion/youtube_ingestor.py` (yt-dlp transcript pipeline)
- [x] **Task 3.4** — Write `src/ingestion/auto_tagger.py` (domain + content type classifier)
- [x] **Task 3.5** — Write `tests/test_phase3.py` and pass all acceptance tests
**Phase:** 4 — Voice Layer (100% complete)

---

## Phase 4 Tasks (complete)

- [x] **Task 4.1** — Install + benchmark faster-whisper on CUDA (target: <200ms for 5s clip)
- [x] **Task 4.2** — Write `src/voice/vad.py` (Silero VAD recording loop)
- [x] **Task 4.3** — Write `src/voice/stt.py` (faster-whisper transcription service)
- [x] **Task 4.4** — Write `src/voice/tts.py` (Kokoro ONNX streaming playback)
- [x] **Task 4.5** — Write `src/voice/pipeline.py` (full VAD → STT → Brain → TTS loop)
- [x] **Task 4.6** — Add hotkey trigger (Ctrl+Space via pynput)
- [x] **Task 4.7** — Write `tests/test_phase4.py` (latency benchmark: must be <1.5s end-to-end)

---

## Phase 5 Tasks (do not start until Phase 4 is 100% complete)

- [ ] **Task 5.1** — Write `src/agents/planner.py` (goal → task breakdown)
- [ ] **Task 5.2** — Write `src/agents/sub_agent.py` (isolated context window executor)
- [ ] **Task 5.3** — Configure Bytebot Docker sandbox
- [ ] **Task 5.4** — Write `src/agents/proactive.py` (window title monitor + notification)
- [ ] **Task 5.5** — Write `tests/test_phase5.py`

---

## Blocked Tasks

None

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
| 2026-06-06 | TTS Streaming Optimization | Refactored `src/voice/tts.py` to use sentence-level streaming. Audio starts playing as soon as the first sentence is ready. Achieved 791ms E2E latency on benchmark. |
| 2026-06-06 | Phase 4 complete | Implemented Voice Layer (VAD, STT, TTS, Pipeline, Hotkey). Resolved NumPy 2.x and PortAudio dependencies. Achieved 802ms end-to-end latency (target <1500ms). Verified all Phase 4 tests pass. |
| 2026-06-06 | Phase 3 completion | Created standalone AutoTagger in `src/ingestion/auto_tagger.py` and refactored `src/ingestion/chunker.py` to use it. Added unit tests for classification, German, and Arabic. Verified all 47 tests pass. Phase 3 is 100% complete. |
| 2026-06-06 | Phase 3 Task 3.3 | Implemented YouTube transcript downloader and WebVTT cleaning parser in `src/ingestion/youtube_ingestor.py`. Added POST /ingest/youtube FastAPI route in `src/ingestion/web_endpoint.py` and integrated it with background pipeline ingestion. Updated `docs/BOOKMARKLET.md` and verified all 46 tests pass. |
| 2026-06-06 | Phase 3 Task 3.1 & 3.2 | Implemented FastAPI /ingest/web endpoint in `src/ingestion/web_endpoint.py` and bookmarklet script in `docs/BOOKMARKLET.md`. Integrated automated summary generation in `src/ingestion/pipeline.py` and verified 3 integration tests. |
| 2026-06-06 | Phase 2 environment & test verification | Verified local Python 3.10.12 env setup, ran and passed all 7 acceptance tests in `tests/test_phase2.py`. Phase 2 is 100% complete. |
| 2026-06-06 | Phase 2 implementation | Added Letta-aware core memory sync, deterministic daily review generation, daily review extraction, persistent mistake tracking, and new `tests/test_phase2.py`. |
| 2026-06-06 | Phase 1 environment & test verification | Verified local Python 3.10.12 env setup, fixed query rendering test in `tests/test_query_rendering.py`, verified all 120 tests pass successfully. Phase 1 is 100% complete. |
| 2026-06-06 | Phase 1 implementation in progress | Core ingestion modules, CLI, and supporting tests/docs were added; runtime validation remains blocked by the Python environment. |
| 2026-06-06 | Documentation and Missing Scripts | Created scripts/run_unit_subset.sh and 5 key documentation files (ENVIRONMENT_MATRIX.md, INGESTION_FLOW.md, PRIVACY_MODEL.md, VECTOR_STORE_NOTES.md, WATCHER_BEHAVIOR.md). |
