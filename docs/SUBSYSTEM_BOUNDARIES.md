# Subsystem Boundaries and Ownership Rules

## Purpose

This document defines the canonical subsystem boundaries for the Personal AI Brain at the start of Phase 6.
It follows [docs/RUNTIME_TOPOLOGY.md](./RUNTIME_TOPOLOGY.md) and turns the observed runtime into explicit ownership rules.

This is the reference artifact for Phase 6 Task `6.1.2`.

---

## Boundary Principles

These rules apply across the whole system:

1. Each subsystem has one primary owner and one clear responsibility.
2. Cross-subsystem communication should happen through explicit interfaces, not ad hoc imports.
3. Transport layers should not own business logic.
4. Long-running external dependencies must be wrapped by narrow adapters.
5. Tool execution policy must be centralized, not redefined per caller.
6. UI, control, and orchestration should be separate concerns even if they temporarily share a process.

---

## Canonical Subsystems

### 1. Voice Subsystem

Owned by:

- `src/voice/daemon.py`
- `src/voice/vad.py`
- `src/voice/stt.py`
- `src/voice/tts.py`
- `src/voice/hotkey.py`

Owns:

- microphone capture
- wake-word detection
- VAD lifecycle
- STT transcription
- TTS playback
- local audio state
- interruption primitives

Must not own:

- provider selection
- planner execution
- memory routing
- retrieval policy
- dashboard/UI behavior

Public contract:

- emits normalized transcript events
- receives normalized speak/status/control events

Future preferred interface:

- typed event schema between voice daemon and control/API plane

Ownership rule:

If a change concerns audio capture, audio playback, mic state, interruption, or speech timing, it belongs here.
If it concerns what the assistant should do with the words, it does not belong here.

### 2. API / Control Plane Subsystem

Owned by:

- `src/api/main.py`
- `src/api/ws_manager.py`
- `src/api/dashboard.py`
- `src/api/privacy_router.py`
- dashboard templates and static assets

Owns:

- HTTP endpoints
- WebSocket endpoints
- dashboard transport
- health/status endpoints
- request validation and response shaping
- top-level service orchestration hooks

Must not own:

- detailed identity/provider logic
- planner internals
- retrieval implementation details
- audio behavior

Public contract:

- HTTP API
- WebSocket API
- control-plane state exposure

Ownership rule:

The API layer is the transport and supervision layer.
It may coordinate subsystems, but it should not permanently contain subsystem-specific logic like inline identity routing.

### 3. Identity Subsystem

Owned by:

- future dedicated `IdentityManager` module
- `src/memory/letta_agent.py`
- `src/memory/openclaw_agent.py`
- provider selection logic currently embedded in `src/api/main.py`

Owns:

- assistant identity
- system prompt composition
- provider fallback rules
- conversational response policy
- identity-level memory sync hooks

Must not own:

- HTTP transport
- voice transport
- raw planner loop
- direct database storage logic outside defined interfaces

Public contract:

- `respond(message, context)`
- `health()`
- `warmup()`
- `sync_memory()`

Ownership rule:

Anything that answers “who is speaking as the brain” or “which provider should answer this” belongs here.
This should become one canonical subsystem rather than being split across API branches.

### 4. Memory Subsystem

Owned by:

- `src/memory/core_memory.py`
- `src/memory/daily_review.py`
- `src/memory/extractor.py`
- `src/memory/mistake_tracker.py`

Owns:

- local durable memory files
- memory schema and persistence
- daily review generation
- extraction of durable updates
- mistake logging and recall

Must not own:

- HTTP routing
- voice playback/capture
- planner tool policy
- direct dashboard behavior

Public contract:

- structured memory read/write APIs
- review generation
- update extraction
- mistake search/check APIs

Ownership rule:

If the concern is persistence of personal state across sessions, it belongs here.
If the concern is reasoning over that memory in conversation, that belongs to Identity.

### 5. Retrieval / Ingestion Subsystem

Owned by:

- `src/ingestion/*`

Owns:

- file watching
- extraction
- chunking
- auto-tagging
- embeddings
- vector store writes
- hybrid search implementation
- ingestion endpoints
- YouTube and web ingestion

Must not own:

- conversation policy
- planner orchestration
- audio logic
- dashboard rendering

Public contract:

- ingest operations
- search operations
- retrieval-ready metadata

Ownership rule:

This subsystem is the knowledge acquisition and retrieval engine.
It should remain one of the cleanest boundaries in the codebase and avoid absorbing assistant logic.

### 6. Planner / Agency Subsystem

Owned by:

- `src/agents/planner.py`
- `src/agents/sub_agent.py`
- `src/agents/confirmation.py`
- `src/agents/base.py`

Owns:

- goal decomposition
- think/act/observe execution
- sub-agent delegation
- confirmation gates
- planner traces
- tool invocation sequencing

Must not own:

- direct audio state
- transport endpoints
- low-level model provider routing
- raw retrieval storage

Public contract:

- `execute(goal)`
- sub-agent task execution
- structured planner trace output

Ownership rule:

If the problem is “how do we complete this task safely using tools,” it belongs here.
If the problem is “which model/provider speaks as Omar,” it belongs to Identity.

### 7. Tooling / Host Integration Subsystem

Owned by:

- `src/agents/tools/*`

Owns:

- tool interfaces
- tool registry
- host integrations
- sandbox adapters
- browser adapters
- screen capture adapters
- command execution adapters

Must not own:

- planner logic
- identity policy
- UI routing
- memory schema

Public contract:

- stable tool interface
- tool capability metadata
- safety classification metadata

Ownership rule:

Tools are adapters around capabilities.
They should expose actions cleanly, not decide when those actions are appropriate.

### 8. External Services Subsystem

Owned adapters:

- Ollama adapter usage
- Letta adapter usage
- Bytebot adapter usage
- OpenClaw CLI bridge
- optional Gemini/provider bridges

Owns:

- dependency-specific connection details
- health checks
- request normalization to third-party/local services

Must not own:

- high-level business rules
- user-facing orchestration policy

Ownership rule:

Every external system should be wrapped so the rest of the code does not depend on vendor/runtime quirks directly.

---

## Allowed Dependency Directions

The intended dependency direction is:

```text
UI / Voice Clients
        ↓
API / Control Plane
        ↓
Identity / Planner
        ↓
Memory / Retrieval / Tools
        ↓
External Services and Local Storage
```

Allowed:

- API calling Identity
- API calling Planner
- Planner calling Tools
- Identity calling Memory
- Identity calling external-provider adapters
- Tools calling Retrieval or external adapters

Not preferred:

- Voice directly importing planner logic
- Tools deciding provider routing
- API embedding large provider-switch condition trees
- Retrieval depending on identity or UI
- Memory directly controlling planner behavior

---

## Ownership Matrix

### Voice

- Owner: Voice subsystem
- Secondary collaborators: API/control plane
- Forbidden leakage: provider routing and planner decisions

### Search and ingestion

- Owner: Retrieval/ingestion subsystem
- Secondary collaborators: API, tools, identity
- Forbidden leakage: conversational policy

### Assistant response selection

- Owner: Identity subsystem
- Secondary collaborators: memory, API
- Forbidden leakage: voice transport and tool implementation

### Task execution

- Owner: Planner/agency subsystem
- Secondary collaborators: tools, memory, retrieval
- Forbidden leakage: transport-layer branching

### Tool permission policy

- Owner: Planner/tool policy boundary
- Secondary collaborators: confirmation gate, sandbox
- Forbidden leakage: per-tool ad hoc approval logic

### Health and operations

- Owner: API/control plane plus common health utilities
- Secondary collaborators: service adapters
- Forbidden leakage: random subsystem-local health conventions

---

## Current Violations Against the Target Boundaries

These are the important current violations revealed by the runtime topology:

### 1. API owns too much identity logic

Current issue:

- `src/api/main.py` contains inline `IdentityManager` logic and provider branching.

Target:

- move that into a dedicated identity subsystem module

### 2. Planner tools mix safety levels without a formal class model

Current issue:

- retrieval, notifications, browser, sandbox, shell, and screen capture are all peers in one registry without a canonical safety taxonomy

Target:

- define tool classes and permission policy centrally

### 3. Voice daemon contract is too thin

Current issue:

- current WebSocket messages are effectively string payloads with minimal state semantics

Target:

- define canonical event types and state transitions

### 4. External adapters are inconsistent

Current issue:

- some dependencies are wrapped cleanly, others are invoked directly or implicitly

Target:

- unify service adapters and runtime health interfaces

### 5. Host integrations are not yet a coherent boundary

Current issue:

- desktop/system actions are spread across tools and scripts

Target:

- make host integration an explicit adapter layer under the tools subsystem

---

## Ownership Rules for Concurrent AI Work

Because multiple AI agents may work in parallel, use these rules:

1. Prefer new design docs for architecture tasks before modifying shared runtime files.
2. Treat `src/api/main.py`, `src/voice/daemon.py`, `src/agents/tools/__init__.py`, and provider adapters as high-conflict files.
3. Do not combine architectural refactors and feature work in the same change unless explicitly coordinated.
4. Before editing a shared runtime file, inspect `git status --short`.
5. For Phase 6 architecture tasks, create standalone artifacts first, then refactor code in smaller follow-up tasks.

This is the recommended coordination discipline for the rest of Phase 6.

---

## Immediate Next Step

The next architectural move should be to translate these ownership rules into:

- a dedicated `IdentityManager` module boundary
- a voice event schema
- a planner state model
- a tool safety taxonomy

Those items map directly to the next Phase 6 runtime-hardening tasks.
