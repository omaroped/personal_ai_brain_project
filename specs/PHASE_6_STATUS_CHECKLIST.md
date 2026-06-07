# STATUS FORMAT — Phase 6 Execution Checklist
# Mirrors the task style used in STATUS.md so this can be copied into the tracker later.

---

## Phase 6 Tasks — Optimization, Hardening, and Open-Source Readiness

### 6.1 — Runtime Architecture Hardening

- [ ] **Task 6.1.1** — Write a runtime topology map covering Voice, API, Memory, Planner, Tools, and external services
- [ ] **Task 6.1.2** — Define canonical subsystem boundaries and ownership rules
- [ ] **Task 6.1.3** — Refactor the voice pipeline into a dedicated `voice-daemon` service boundary
- [ ] **Task 6.1.4** — Define `VoiceEvent`, `VoiceCommand`, and playback/interruption state schemas
- [ ] **Task 6.1.5** — Implement IPC between `voice-daemon` and Brain API via WebSocket or equivalent transport
- [ ] **Task 6.1.6** — Ensure voice daemon can restart independently without crashing planner or memory services
- [ ] **Task 6.1.7** — Build `IdentityManager` interface for provider selection, fallback, and memory sync
- [ ] **Task 6.1.8** — Migrate voice and API layers to use `IdentityManager` instead of direct provider branching
- [ ] **Task 6.1.9** — Refactor planner loop into explicit state machine with guarded transitions
- [ ] **Task 6.1.10** — Add planner execution traces with per-state logging and failure recovery paths
- [ ] **Task 6.1.11** — Build a control-plane module/API for service health, provider state, voice state, and planner traces

### 6.2 — Reliability and Observability

- [ ] **Task 6.2.1** — Standardize structured logging across ingestion, memory, voice, planner, tools, and API
- [ ] **Task 6.2.2** — Add trace IDs for every end-to-end user interaction
- [ ] **Task 6.2.3** — Correlate STT, routing, retrieval, tool use, response generation, and TTS under the same trace
- [ ] **Task 6.2.4** — Define performance budgets for wake-word, STT, retrieval, planning, TTS, and full roundtrip latency
- [ ] **Task 6.2.5** — Add automated benchmark scripts for mean, p95, memory, CPU, and GPU measurements
- [ ] **Task 6.2.6** — Build long-run stability tests for idle runtime, repeated voice interactions, and session durability
- [ ] **Task 6.2.7** — Add recovery tests for service restart, degraded dependencies, and Letta/Ollama temporary outages
- [ ] **Task 6.2.8** — Verify memory persistence and planner resilience across restart events

### 6.3 — Dependency and Environment Simplification

- [ ] **Task 6.3.1** — Audit all heavyweight dependencies and classify them as core, optional, or experimental
- [ ] **Task 6.3.2** — Split dependency installation into capability-based profiles (`core`, `voice`, `agents`, `dev`)
- [ ] **Task 6.3.3** — Standardize one supported Python version and document it clearly
- [ ] **Task 6.3.4** — Build an environment validation command for Python, venv, Ollama, Letta, models, audio stack, and writable paths
- [ ] **Task 6.3.5** — Remove or abstract remaining hardcoded local paths such as `/home/omar/...`
- [ ] **Task 6.3.6** — Make path configuration portable through config defaults and env overrides
- [ ] **Task 6.3.7** — Verify that a clean machine can bootstrap the project without manual path surgery

### 6.4 — Open-Source Productization

- [ ] **Task 6.4.1** — Rewrite `README.md` to reflect the real current system instead of earlier project state
- [ ] **Task 6.4.2** — Define the project’s public one-sentence identity and align docs to it
- [ ] **Task 6.4.3** — Add a trustworthy Quickstart with one blessed setup path
- [ ] **Task 6.4.4** — Add a smoke-test flow for the three core demos: ingest/query, memory review, and voice response
- [ ] **Task 6.4.5** — Add open-source hygiene files: `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue/PR templates
- [ ] **Task 6.4.6** — Add changelog and release-note conventions
- [ ] **Task 6.4.7** — Add CI pipeline for lint, import/type checks, core tests, and smoke-safe acceptance tests
- [ ] **Task 6.4.8** — Separate stable vs experimental modules in documentation
- [ ] **Task 6.4.9** — Confirm a new external contributor can install and run the core system from docs alone

### 6.5 — Security and Safety Hardening

- [ ] **Task 6.5.1** — Define tool classes: read-only, local-write, system-control, networked, destructive
- [ ] **Task 6.5.2** — Add confirmation and audit policies per tool class
- [ ] **Task 6.5.3** — Verify privacy routing guarantees for local-only sensitive domains under all provider modes
- [ ] **Task 6.5.4** — Harden secret handling for API keys, auth tokens, and provider mode switches
- [ ] **Task 6.5.5** — Write a concise threat model for prompt injection, tool misuse, browser content, and data exfiltration
- [ ] **Task 6.5.6** — Verify sandbox guarantees for filesystem, localhost isolation, network limits, and timeouts
- [ ] **Task 6.5.7** — Add tests proving destructive actions cannot bypass confirmation gates

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

- [ ] **Task 6.7.1** — Standardize top-level commands: `make setup`, `make health`, `make test`, `make smoke`, `make run-api`, `make run-voice`
- [ ] **Task 6.7.2** — Maintain a short and accurate repo architecture map for contributors
- [ ] **Task 6.7.3** — Document which tests require audio, GPU, external services, or pure local unit-only execution
- [ ] **Task 6.7.4** — Clarify public/stable interfaces vs internal/experimental modules
- [ ] **Task 6.7.5** — Add contributor-friendly dev environment guidance and troubleshooting flow

### 6.8 — Phase 6 Acceptance and Release Readiness

- [ ] **Task 6.8.1** — Run full regression suite after Phase 6 architecture refactors
- [ ] **Task 6.8.2** — Run benchmark suite and confirm no regression against Phase 4/5 latency targets without explanation
- [ ] **Task 6.8.3** — Validate the three public demo flows from a clean setup path
- [ ] **Task 6.8.4** — Verify documentation matches actual runtime behavior and current repo state
- [ ] **Task 6.8.5** — Tag a release candidate (`v0.1.0-rc1` or equivalent) and review for open-source publication quality
- [ ] **Task 6.8.6** — Publish Phase 6 completion notes and define post-Phase-6 roadmap

---

## Suggested STATUS.md Summary Line

**Phase:** 6 — Optimization, Hardening, and Open-Source Readiness  
**Active Spec:** `specs/PHASE_6_OPTIMIZATION_PLAN.md`  
**Overall Progress:** 0% (Phase 6 not started)

