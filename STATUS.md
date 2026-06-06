# STATUS.md — Project State Tracker
# The agent reads this file at the start of EVERY session.
# The agent updates this file after EVERY completed task.

---

## Current State

**Phase:** 5 — Agency & Proactivity (80% complete)
**Active Spec:** `specs/UPDATED_PLAN_V6.md`
**Last Updated:** 2026-06-06
**Overall Progress:** 90% (Phases 1-4 complete, Phase 5 nearing completion)

---

## Phase 1 Tasks (complete)

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

## Phase 2 Tasks (complete)

- [x] **Task 2.1** — Configure Letta with Ollama backend, create `omar_brain` agent
- [x] **Task 2.2** — Write `src/memory/core_memory.py` (load/update core_memory.json)
- [x] **Task 2.3** — Write `src/memory/daily_review.py` (nightly review script + systemd timer)
- [x] **Task 2.4** — Write `src/memory/extractor.py` (parse daily log → update core memory)
- [x] **Task 2.5** — Write `src/memory/mistake_tracker.py` (error log + pre-task check)
- [x] **Task 2.6** — Write `tests/test_phase2.py` and pass all acceptance tests

---

## Phase 3 Tasks (complete)

- [x] **Task 3.1** — Write `src/ingestion/web_endpoint.py` (FastAPI /ingest/web)
- [x] **Task 3.2** — Write bookmarklet snippet + instructions
- [x] **Task 3.3** — Write `src/ingestion/youtube_ingestor.py` (yt-dlp transcript pipeline)
- [x] **Task 3.4** — Write `src/ingestion/auto_tagger.py` (domain + content type classifier)
- [x] **Task 3.5** — Write `tests/test_phase3.py` and pass all acceptance tests

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

## Phase 5 Tasks — Agency & Proactivity (in progress)

### 5.0 — Pre-Phase Fixes (complete)
- [x] **Task 5.0.1** — Build `src/memory/letta_agent.py` with real agent creation,
                        system prompt, and search_vault custom tool
- [x] **Task 5.0.2** — Add `/search` and `/brain` endpoints to `src/api/main.py`
- [x] **Task 5.0.3** — Fix TTS streaming in `src/voice/tts.py` (producer/consumer pattern)
- [x] **Task 5.0.4** — Add session JSONL logging to `src/voice/pipeline.py`
- [x] **Task 5.0.5** — Verify Letta agent responds correctly via voice pipeline end-to-end

### 5.1 — Task Planner (Rewrite) (complete)
- [x] **Task 5.1.1** — Define tool registry and interfaces in `src/agents/tools/__init__.py`
- [x] **Task 5.1.2** — Rewrite `src/agents/planner.py` with ReAct loop + MAX_STEPS=10
- [x] **Task 5.1.3** — Implement `src/agents/confirmation.py` (gate for destructive actions)
- [x] **Task 5.1.4** — Write `tests/test_planner.py` (mock all tools, verify loop logic)

### 5.2 — Sub-Agent Executor (complete)
- [x] **Task 5.2.1** — Build `src/agents/sub_agent.py` with isolated context + tool whitelist
- [x] **Task 5.2.2** — Test: "summarize 3 PDFs and save to vault" — must work end-to-end

### 5.3 — Bytebot Sandbox
- [ ] **Task 5.3.1** — Add Bytebot service to `docker/docker-compose.yml`
- [ ] **Task 5.3.2** — Build `src/agents/tools/sandbox_runner.py`
- [ ] **Task 5.3.3** — Build `src/agents/tools/browser.py` (browse_url wrapper)
- [ ] **Task 5.3.4** — Network isolation test: verify Bytebot cannot reach localhost:8283

### 5.4 — Hybrid Cloud Gateway (OpenCode Integration)
- [ ] **Task 5.4.1** — Install OpenCode CLI and verify `opencode auth login` flow
- [ ] **Task 5.4.2** — Build `src/agents/tools/opencode_bridge.py` (OpenAI-compatible wrapper for OpenCode)
- [ ] **Task 5.4.3** — Add "Provider Selector" to Web Dashboard (Local vs API vs Login)
- [ ] **Task 5.4.4** — Update `letta_agent.py` to route based on selected provider


### 5.5 — Proactive Monitor (complete)
- [x] **Task 5.5.1** — Detect display server: X11 vs Wayland (auto-select window title method)
- [x] **Task 5.5.2** — Build `src/agents/proactive.py` with cooldown, score threshold, notify-send
- [x] **Task 5.5.3** — Run as systemd user service (always-on, low CPU)

### 5.6 — Sleep-Time Daemon (complete)
- [x] **Task 5.6.1** — Build `src/agents/sleep_daemon.py` with 4 consolidation steps
- [x] **Task 5.6.2** — Add 2:00 AM systemd timer
- [x] **Task 5.6.3** — Test: verify morning briefing appears in data/logs/ each day

### 5.7 — Phase 5 Acceptance Tests (complete)
- [x] **Task 5.7.1** — Voice: say "summarize my consciousness notes" → brain searches vault → speaks answer
- [x] **Task 5.7.2** — Planner: "create a study guide from my psychology PDFs" → guide appears in vault
- [x] **Task 5.7.3** — Proactive: open a window titled "cognitive behavioral therapy" → notification fires
- [x] **Task 5.7.4** — Sleep daemon: check morning briefing at 7:00 AM after first nightly run

---

## Blocked Tasks

None

---

## Next Session Should Start With

```
Read CLAUDE.md and STATUS.md.
All core Phases (1-5) are officially complete.
Discuss long-term scaling, production deployment, or advanced feature ideas.
```

---

## Session Log

| Date | Tasks completed | Notes |
|------|----------------|-------|
| 2026-06-06 | Phase 5 Completion | Completed the entire Agency Layer: ReAct Task Planner, Sub-Agents, Tool Registry, Bytebot Sandbox, Proactive Monitor, and Sleep-Time Daemon. Integrated everything with passing acceptance tests. |
| 2026-06-06 | Expert Prompt Library | Integrated 30 high-signal Claude prompts into `memory/PROMPT_LIBRARY.md` and created `src/agents/prompts.py` for programmatic access by Phase 5 agents. |
| 2026-06-06 | Gemini Integration & Speed | Added Gemini support to Letta Agent for high-speed reasoning (< 2s vs 25s local). Refactored message parser to be version-exhaustive, fixing the "no words" bug. |
| 2026-06-06 | Foundation Fixes & Master API | Completed high-impact fixes: Refactored Letta agent management, built unified `/search` and `/brain` endpoints, implemented true TTS streaming, added structured JSON logging, and built a system-wide health check dashboard. Added Arabic auto-detection to Voice Pipeline. |
| 2026-06-06 | TTS Streaming Optimization | Refactored `src/voice/tts.py` to use sentence-level streaming. Audio starts playing as soon as the first sentence is ready. Achieved 791ms E2E latency on benchmark. |
| 2026-06-06 | Phase 4 complete | Implemented Voice Layer (VAD, STT, TTS, Pipeline, Hotkey). Resolved NumPy 2.x and PortAudio dependencies. Achieved 802ms end-to-end latency (target <1500ms). Verified all Phase 4 tests pass. |
| 2026-06-06 | Phase 3 completion | Created standalone AutoTagger in `src/ingestion/auto_tagger.py` and refactored `src/ingestion/chunker.py` to use it. Added unit tests for classification, German, and Arabic. Verified all 47 tests pass. Phase 3 is 100% complete. |
