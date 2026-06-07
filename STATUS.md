# STATUS.md — Project State Tracker
# The agent reads this file at the start of EVERY session.
# The agent updates this file after EVERY completed task.

---

## Current State

**Phase:** 6 — Optimization, Hardening, and Open-Source Readiness
**Active Spec:** `specs/PHASE_6_OPTIMIZATION_PLAN.md`
**Last Updated:** 2026-06-07
**Overall Progress:** 50% (Phase 6 in progress; runtime boundaries, planner state machine, dependency profiles, CI, portability cleanup, contributor docs, and core safety/privacy policy completed)

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

## Phase 5 Tasks — Agency & Proactivity (complete)

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

### 5.3 — Bytebot Sandbox (complete)
- [x] **Task 5.3.1** — Add Bytebot service to `docker/docker-compose.yml`
- [x] **Task 5.3.2** — Build `src/agents/tools/sandbox_runner.py`
- [x] **Task 5.3.3** — Build `src/agents/tools/browser.py` (browse_url wrapper)
- [x] **Task 5.3.4** — Network isolation test: verify Bytebot cannot reach localhost:8283

### 5.4 — Hybrid Cloud Gateway (OpenCode Integration) (complete)
- [x] **Task 5.4.1** — Install OpenCode CLI and verify `opencode auth login` flow
- [x] **Task 5.4.2** — Build `src/agents/tools/opencode_bridge.py` (OpenAI-compatible wrapper for OpenCode)
- [x] **Task 5.4.3** — Add "Provider Selector" to Web Dashboard (Local vs API vs Login)
- [x] **Task 5.4.4** — Update `letta_agent.py` to route based on selected provider


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

## Phase 6 Tasks — Optimization, Hardening, and Open-Source Readiness

### 6.1 — Runtime Architecture Hardening

- [x] **Task 6.1.1** — Write a runtime topology map covering Voice, API, Memory, Planner, Tools, and external services
- [x] **Task 6.1.2** — Define canonical subsystem boundaries and ownership rules
- [x] **Task 6.1.3** — Refactor the voice pipeline into a dedicated `voice-daemon` service boundary
- [x] **Task 6.1.4** — Define `VoiceEvent`, `VoiceCommand`, and playback/interruption state schemas
- [x] **Task 6.1.5** — Implement IPC between `voice-daemon` and Brain API via WebSocket or equivalent transport
- [ ] **Task 6.1.6** — Ensure voice daemon can restart independently without crashing planner or memory services
- [x] **Task 6.1.7** — Build `IdentityManager` interface for provider selection, fallback, and memory sync
- [x] **Task 6.1.8** — Migrate voice and API layers to use `IdentityManager` instead of direct provider branching
- [x] **Task 6.1.9** — Refactor planner loop into explicit state machine with guarded transitions
- [x] **Task 6.1.10** — Add planner execution traces with per-state logging and failure recovery paths
- [x] **Task 6.1.11** — Build a control-plane module/API for service health, provider state, voice state, and planner traces

### 6.2 — Reliability and Observability

- [x] **Task 6.2.1** — Standardize structured logging across ingestion, memory, voice, planner, tools, and API
- [ ] **Task 6.2.2** — Add trace IDs for every end-to-end user interaction
- [ ] **Task 6.2.3** — Correlate STT, routing, retrieval, tool use, response generation, and TTS under the same trace
- [x] **Task 6.2.4** — Define performance budgets for wake-word, STT, retrieval, planning, TTS, and full roundtrip latency
- [x] **Task 6.2.5** — Add automated benchmark scripts for mean, p95, memory, CPU, and GPU measurements
- [ ] **Task 6.2.6** — Build long-run stability tests for idle runtime, repeated voice interactions, and session durability
- [ ] **Task 6.2.7** — Add recovery tests for service restart, degraded dependencies, and Letta/Ollama temporary outages
- [ ] **Task 6.2.8** — Verify memory persistence and planner resilience across restart events

### 6.3 — Dependency and Environment Simplification

- [x] **Task 6.3.1** — Audit all heavyweight dependencies and classify them as core, optional, or experimental
- [x] **Task 6.3.2** — Split dependency installation into capability-based profiles (`core`, `voice`, `agents`, `dev`)
- [x] **Task 6.3.3** — Standardize one supported Python version and document it clearly
- [x] **Task 6.3.4** — Build an environment validation command for Python, venv, Ollama, Letta, models, audio stack, and writable paths
- [x] **Task 6.3.5** — Remove or abstract remaining hardcoded local paths such as `/home/omar/...`
- [x] **Task 6.3.6** — Make path configuration portable through config defaults and env overrides
- [ ] **Task 6.3.7** — Verify that a clean machine can bootstrap the project without manual path surgery

### 6.4 — Open-Source Productization

- [x] **Task 6.4.1** — Rewrite `README.md` to reflect the real current system instead of earlier project state
- [x] **Task 6.4.2** — Define the project’s public one-sentence identity and align docs to it
- [x] **Task 6.4.3** — Add a trustworthy Quickstart with one blessed setup path
- [x] **Task 6.4.4** — Add a smoke-test flow for the three core demos: ingest/query, memory review, and voice response
- [x] **Task 6.4.5** — Add open-source hygiene files: `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue/PR templates
- [x] **Task 6.4.6** — Add changelog and release-note conventions
- [x] **Task 6.4.7** — Add CI pipeline for lint, import/type checks, core tests, and smoke-safe acceptance tests
- [x] **Task 6.4.8** — Separate stable vs experimental modules in documentation
- [ ] **Task 6.4.9** — Confirm a new external contributor can install and run the core system from docs alone

### 6.5 — Security and Safety Hardening

- [x] **Task 6.5.1** — Define tool classes: read-only, local-write, system-control, networked, destructive
- [x] **Task 6.5.2** — Add confirmation and audit policies per tool class
- [x] **Task 6.5.3** — Verify privacy routing guarantees for local-only sensitive domains under all provider modes
- [ ] **Task 6.5.4** — Harden secret handling for API keys, auth tokens, and provider mode switches
- [x] **Task 6.5.5** — Write a concise threat model for prompt injection, tool misuse, browser content, and data exfiltration
- [ ] **Task 6.5.6** — Verify sandbox guarantees for filesystem, localhost isolation, network limits, and timeouts
- [x] **Task 6.5.7** — Add tests proving destructive actions cannot bypass confirmation gates

### 6.6 — Jarvis-Tier Feature Layer

- [ ] **Task 6.6.1** — Implement true barge-in support with continuous buffering and TTS interruption handling
- [ ] **Task 6.6.2** — Add voice-state machine support for interruption, cancellation, and resumed listening
- [ ] **Task 6.6.3** — Build `CaptureScreenTool` with backend abstraction for X11 and Wayland
- [ ] **Task 6.6.4** — Add opt-in screen-awareness flow with explicit visibility and audit logging
- [ ] **Task 6.6.5** — Integrate a local vision-model adapter for screen description
- [ ] **Task 6.6.6** — Replace broad shell execution with specialized OS tools: window, clipboard, media, notification, file organization
- [ ] **Task 6.6.7** — Build personal context fusion from active app, planner state, memory, mistakes, and recent retrievals
- [ ] **Task 6.6.8** — Upgrade morning briefing generation with unresolved tasks, reminders, and personalized suggestions

### 6.7 — Developer Experience

- [x] **Task 6.7.1** — Standardize top-level commands: `make setup`, `make health`, `make test`, `make smoke`, `make run-api`, `make run-voice`
- [x] **Task 6.7.2** — Maintain a short and accurate repo architecture map for contributors
- [x] **Task 6.7.3** — Document which tests require audio, GPU, external services, or pure local unit-only execution
- [x] **Task 6.7.4** — Clarify public/stable interfaces vs internal/experimental modules
- [x] **Task 6.7.5** — Add contributor-friendly dev environment guidance and troubleshooting flow

### 6.8 — Phase 6 Acceptance and Release Readiness

- [ ] **Task 6.8.1** — Run full regression suite after Phase 6 architecture refactors
- [ ] **Task 6.8.2** — Run benchmark suite and confirm no regression against Phase 4/5 latency targets without explanation
- [ ] **Task 6.8.3** — Validate the three public demo flows from a clean setup path
- [ ] **Task 6.8.4** — Verify documentation matches actual runtime behavior and current repo state
- [ ] **Task 6.8.5** — Tag a release candidate (`v0.1.0-rc1` or equivalent) and review for open-source publication quality
- [ ] **Task 6.8.6** — Publish Phase 6 completion notes and define post-Phase-6 roadmap

---

## Blocked Tasks

None

---

## Next Session Should Start With

```
Read CLAUDE.md and STATUS.md.
Tell me what phase we are in and what the first uncompleted task is.
Then begin Phase 6 in strict task order, starting with Task 6.1.6.
```

---

## Session Log

| Date | Tasks completed | Notes |
|------|----------------|-------|
| 2026-06-07 | Phase 6 developer ergonomics | Reflected the existing top-level command surface from the workspace `Makefile` in the tracker and aligned it with the broader Phase 6 DX work. |
| 2026-06-07 | Phase 6 observability baseline | Documented the existing structured logging, planner traces, voice trace IDs, and control-plane status surface in `docs/OBSERVABILITY.md`. |
| 2026-06-07 | Phase 6 privacy verification | Extended `tests/test_privacy_router.py` to cover cloud-enabled routing cases, proving that sensitive domains remain local while allowed domains can route to cloud when enabled. |
| 2026-06-07 | Phase 6 safety and portability batch | Added env-overridable runtime paths in `config.py`, removed remaining hardcoded runtime `/home/omar` paths, added `src/agents/tool_policy.py`, integrated confirmation policy by tool risk class, added `tests/test_tool_policy.py`, and wrote `docs/THREAT_MODEL.md`. |
| 2026-06-07 | Phase 6 docs and smoke-flow batch | Added `docs/SMOKE_FLOWS.md`, `docs/REPO_MAP.md`, and cleaned bookmarklet setup docs. Marked README/identity/quickstart/product smoke-flow tasks complete based on the current repo state and supporting artifacts. |
| 2026-06-07 | Phase 6 packaging and governance batch | Added dependency profiles (`requirements-core.txt`, `requirements-voice.txt`, `requirements-agents.txt`, `requirements-dev.txt`), environment validation script, performance budget and test-matrix docs, interface stability and developer setup docs, open-source hygiene files, and a CI workflow for the CI-safe test lane. |
| 2026-06-07 | Phase 6 planner state machine | Added `src/agents/state_machine.py`, integrated guarded planner state transitions into `BaseAgent`, and added `tests/test_planner_state_machine.py`. |
| 2026-06-07 | Phase 6 runtime hardening batch | Implemented typed voice IPC schemas in `src/voice/protocol.py`, extracted a real `IdentityManager` in `src/identity/manager.py`, migrated API/voice routing to use it, added planner execution traces, and added a `/control/status` control-plane snapshot endpoint. Added `tests/test_phase6_runtime.py` for protocol, identity, trace, and control-plane coverage. |
| 2026-06-07 | Phase 6 Task 6.1.2 | Added `docs/SUBSYSTEM_BOUNDARIES.md` defining canonical subsystem ownership rules, allowed dependency directions, current boundary violations, and concurrency guidance for multi-agent work. |
| 2026-06-07 | Phase 6 Task 6.1.1 | Added `docs/RUNTIME_TOPOLOGY.md` as the current-state runtime topology map covering Voice, API, Memory, Planner, Tools, and external services. |
| 2026-06-07 | Phase 6 planning | Opened Phase 6 as the active phase, added the optimization/hardening/open-source readiness checklist, and normalized STATUS.md to reflect that Phases 1-5 are complete. |
| 2026-06-06 | v0.1.0 Productization | Standardized repo presentation. Completely rewrote `README.md` with clear architecture, constraints, and 'Stable vs Experimental' division. Created `Makefile` for developer ergonomics (`make setup`, `make test`, `make run-voice`). Added `.python-version` file to enforce runtime contract. |
| 2026-06-06 | Phase 5 Completion | Completed the entire Agency Layer: ReAct Task Planner, Sub-Agents, Tool Registry, Bytebot Sandbox, Proactive Monitor, and Sleep-Time Daemon. Integrated everything with passing acceptance tests. |
| 2026-06-06 | Expert Prompt Library | Integrated 30 high-signal Claude prompts into `memory/PROMPT_LIBRARY.md` and created `src/agents/prompts.py` for programmatic access by Phase 5 agents. |
| 2026-06-06 | Gemini Integration & Speed | Added Gemini support to Letta Agent for high-speed reasoning (< 2s vs 25s local). Refactored message parser to be version-exhaustive, fixing the "no words" bug. |
| 2026-06-06 | Foundation Fixes & Master API | Completed high-impact fixes: Refactored Letta agent management, built unified `/search` and `/brain` endpoints, implemented true TTS streaming, added structured JSON logging, and built a system-wide health check dashboard. Added Arabic auto-detection to Voice Pipeline. |
| 2026-06-06 | TTS Streaming Optimization | Refactored `src/voice/tts.py` to use sentence-level streaming. Audio starts playing as soon as the first sentence is ready. Achieved 791ms E2E latency on benchmark. |
| 2026-06-06 | Phase 4 complete | Implemented Voice Layer (VAD, STT, TTS, Pipeline, Hotkey). Resolved NumPy 2.x and PortAudio dependencies. Achieved 802ms end-to-end latency (target <1500ms). Verified all Phase 4 tests pass. |
| 2026-06-06 | Phase 3 completion | Created standalone AutoTagger in `src/ingestion/auto_tagger.py` and refactored `src/ingestion/chunker.py` to use it. Added unit tests for classification, German, and Arabic. Verified all 47 tests pass. Phase 3 is 100% complete. |
