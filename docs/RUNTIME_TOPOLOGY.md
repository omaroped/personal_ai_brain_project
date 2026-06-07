# Runtime Topology

## Purpose

This document captures the actual runtime topology of the Personal AI Brain at the start of Phase 6.
It is not a wish list. It describes the real process boundaries, service dependencies, data flows, and coordination points currently present in the repository.

This is the reference artifact for Phase 6 Task `6.1.1`.

---

## Top-Level Runtime Model

The system currently runs as a multi-process local application with a mix of:

- host Python processes
- Docker services
- local model/runtime services
- desktop/system integrations

At a high level:

1. `src/api/main.py` runs the master FastAPI control plane.
2. `src/voice/daemon.py` runs as an independent voice daemon and talks to the API over WebSockets.
3. Ollama provides local LLM and embedding endpoints.
4. Letta provides persistent agent memory/state through its own server.
5. Bytebot provides isolated execution for selected agent tools.
6. LanceDB persists local semantic retrieval data on disk.

---

## Runtime Nodes

### 1. Master API Process

Primary entrypoint:

- `src/api/main.py`

Primary responsibilities:

- serves HTTP endpoints
- serves dashboard UI/templates/static assets
- mounts ingestion sub-API
- exposes `/health`, `/search`, `/brain`
- terminates WebSocket voice sessions at `/ws/voice`
- routes incoming transcripts through identity/planner logic

Key in-process objects:

- `OmarBrainAgent` from `src/memory/letta_agent.py`
- `OpenClawAgent` from `src/memory/openclaw_agent.py`
- `TaskPlanner` from `src/agents/planner.py`
- inline `IdentityManager` class in `src/api/main.py`
- WebSocket manager from `src/api/ws_manager.py`

Important current property:

The API process is not only an HTTP server. It is also the current orchestration hub for routing, provider selection, and tool-driven action logic.

### 2. Voice Daemon Process

Primary entrypoint:

- `src/voice/daemon.py`

Primary responsibilities:

- microphone/VAD capture
- STT transcription
- TTS playback
- wake-word monitoring
- WebSocket communication with the API

Internal components:

- `VoiceActivityDetector`
- `SpeechToTextService`
- `TextToSpeechService`

Current communication contract:

- sends JSON transcript payloads to `/ws/voice`
- receives JSON TTS response payloads from `/ws/voice`

Important current property:

The voice daemon is already separated into its own process boundary, but the message contract and state model are still thin and informal.

### 3. Ollama Service

External local dependency:

- `http://localhost:11434`

Current responsibilities:

- local chat model backend
- local embedding backend

Used by:

- Letta agent creation/config
- direct local planner/base-agent flows
- embedding and retrieval pipeline
- health checks and setup scripts

### 4. Letta Service

External local dependency:

- `http://localhost:8283`

Container definition:

- `docker/docker-compose.yml`

Current responsibilities:

- persistent agent identity and memory
- long-lived conversational agent state for `omar_brain`

Used by:

- `src/memory/letta_agent.py`
- `/brain` endpoint in `src/api/main.py`
- fallback/default conversational path in API `IdentityManager`

Important current property:

Letta is a real runtime dependency, but the project still keeps provider-routing logic outside Letta and outside a stable identity abstraction.

### 5. Bytebot Service

External container dependency:

- containerized isolated execution environment
- exposed on port `9992`

Container definition:

- `docker/docker-compose.yml`

Current responsibilities:

- sandboxed execution for selected agent tools
- browser/sandbox-oriented sub-agent support

Used by:

- `src/agents/tools/sandbox_runner.py`
- `src/agents/tools/browser.py`
- planner tool calls through the tool registry

### 6. LanceDB Local Storage

Local filesystem dependency:

- `data/vectordb`

Current responsibilities:

- document embeddings
- semantic and hybrid search backing store

Used by:

- ingestion pipeline
- `/search` API endpoint
- `SearchVaultTool`
- Letta custom search path indirectly via API

### 7. OpenClaw CLI Bridge

External host dependency:

- local `openclaw` CLI on `PATH`

Current responsibilities:

- authenticated high-speed reasoning fallback/bypass path

Used by:

- `src/memory/openclaw_agent.py`
- API `IdentityManager`

Important current property:

This is not a network service in the same shape as Ollama or Letta. It is a subprocess integration running inside the API process.

### 8. Desktop/OS Integrations

Host-level dependencies currently used by tools or runtime flows:

- `notify-send`
- `pynput`
- audio stack / sounddevice / PortAudio
- screenshot backends and browser/sandbox tools
- shell command execution

These are not centralized behind a single host-integration boundary yet.

---

## Runtime Boundaries By Layer

### Voice Layer

Owned by:

- `src/voice/daemon.py`
- `src/voice/vad.py`
- `src/voice/stt.py`
- `src/voice/tts.py`

Boundary:

- process-separated from the API
- communicates through WebSocket

Current weakness:

- state transitions are implicit
- interruption/barge-in logic is partial
- echo suppression is still partially behavioral rather than state-driven

### API / Control Layer

Owned by:

- `src/api/main.py`
- `src/api/ws_manager.py`
- dashboard/static/template files

Boundary:

- central process boundary for UI, HTTP, and current orchestration

Current weakness:

- API layer mixes transport, routing, orchestration, and identity logic

### Memory / Identity Layer

Owned by:

- `src/memory/core_memory.py`
- `src/memory/daily_review.py`
- `src/memory/extractor.py`
- `src/memory/mistake_tracker.py`
- `src/memory/letta_agent.py`
- `src/memory/openclaw_agent.py`

Boundary:

- partly local file-based
- partly Letta-backed
- partly provider-routed through API logic

Current weakness:

- no single canonical identity abstraction across Letta, OpenClaw, and optional Gemini routing

### Planning / Agency Layer

Owned by:

- `src/agents/planner.py`
- `src/agents/sub_agent.py`
- `src/agents/confirmation.py`
- `src/agents/tools/*`

Boundary:

- currently in-process with the API
- executes tools through a registry abstraction

Current weakness:

- planner execution is logically structured but not yet modeled as an explicit state graph

### Retrieval / Ingestion Layer

Owned by:

- `src/ingestion/*`

Boundary:

- storage and pipeline layer used by API, planner tools, and memory flows

Current strength:

- this is the cleanest subsystem boundary in the project today

---

## Primary Runtime Flows

### Flow A — Voice Query Roundtrip

1. User speaks into microphone.
2. `VoiceDaemon` captures audio through VAD.
3. `SpeechToTextService` transcribes utterance.
4. Voice daemon sends transcript JSON over WebSocket to `/ws/voice`.
5. API receives transcript.
6. API `IdentityManager.handle_input()` decides whether to route to:
   - `TaskPlanner`
   - `OpenClawAgent`
   - Gemini direct path
   - `OmarBrainAgent` / Letta
7. Response text is produced in the API process.
8. API returns `tts_response` payload over WebSocket.
9. Voice daemon pauses VAD and plays TTS.
10. Voice daemon resumes VAD.

Current critical coupling point:

The routing and “brain” decision happens inside the API process, not inside a dedicated identity/control subsystem.

### Flow B — Semantic Search

1. User or tool calls `/search`.
2. API applies privacy routing decision.
3. API opens `VectorStore`.
4. `VectorStore.hybrid_search()` queries LanceDB-backed data.
5. Results are returned to API caller or tool.

This flow is already relatively clean.

### Flow C — Conversational Brain Query

1. Client POSTs to `/brain`.
2. API ensures Letta agent exists.
3. `OmarBrainAgent.send_message()` sends conversation into Letta.
4. Letta returns message objects.
5. API returns normalized textual response.

Current critical coupling point:

Provider selection and conversational identity policy are not fully isolated from transport concerns.

### Flow D — Planner Tool Execution

1. API or another caller invokes `TaskPlanner.execute(goal)`.
2. Planner uses base-agent loop to request tool calls.
3. Tool registry resolves concrete tool.
4. Tools may call:
   - `/search`
   - local files
   - notifications
   - Bytebot
   - browser wrappers
   - local shell commands
5. Planner returns final answer text.

Current critical coupling point:

Tool safety classes and execution policies are not yet formalized as a runtime-wide permission model.

---

## Current Service Topology Diagram

```text
┌──────────────────────────────┐
│ User / Browser / UI / Voice  │
└──────────────┬───────────────┘
               │
     HTTP      │      WebSocket
               │
┌──────────────▼──────────────────────────────────────┐
│               FastAPI Master API                    │
│  - dashboard                                        │
│  - /health /search /brain                           │
│  - /ws/voice                                        │
│  - current routing/orchestration hub               │
└───────┬───────────────────┬──────────────┬──────────┘
        │                   │              │
        │                   │              │
        │                   │              │
┌───────▼────────┐  ┌───────▼────────┐  ┌──▼─────────────────┐
│ OmarBrainAgent │  │ OpenClawAgent  │  │ TaskPlanner        │
│ (Letta client) │  │ (CLI bridge)   │  │ + Tool Registry    │
└───────┬────────┘  └────────────────┘  └──┬─────────────────┘
        │                                   │
        │                                   │
┌───────▼────────┐                 ┌────────▼────────────┐
│ Letta Server   │                 │ Tools / Sub-Agents  │
│ :8283          │                 │ Bytebot / host ops  │
└────────────────┘                 └─────────────────────┘

┌──────────────────────────────┐
│ Voice Daemon                 │
│ - VAD                        │
│ - STT                        │
│ - TTS                        │
│ - wake-word logic            │
└──────────────┬───────────────┘
               │ WebSocket
               │
               └──────────────► FastAPI /ws/voice

┌──────────────────────────────┐
│ Ollama :11434                │
│ - chat models                │
│ - embeddings                 │
└──────────────────────────────┘

┌──────────────────────────────┐
│ LanceDB on disk              │
│ data/vectordb                │
└──────────────────────────────┘
```

---

## Startup and Operational Entry Points

Primary operator scripts:

- `scripts/start_brain.sh`
- `scripts/brain_status.py`
- `scripts/voice_brain.py`

Operational startup shape today:

1. validate environment
2. start Docker services if needed
3. start FastAPI master API
4. start voice daemon

This is a workable shape, but the process model is still shell-script driven rather than managed through a stronger runtime supervisor/control plane.

---

## Known Coupling Problems Exposed By This Topology

### 1. The API process is overloaded

It currently acts as:

- HTTP transport
- UI server
- WebSocket endpoint
- identity router
- planner host
- agent coordination hub

This is the main architecture pressure point.

### 2. Identity logic is distributed

Identity and response routing currently span:

- inline API `IdentityManager`
- `OmarBrainAgent`
- `OpenClawAgent`
- optional Gemini direct branch

This should become a real subsystem with one stable interface.

### 3. Voice state is not explicit enough

The voice daemon is a separate process, which is good.
But its control model still relies on lightweight flags and behavioral coordination rather than a formal state contract.

### 4. Tool execution classes are not yet first-class

Planner tools currently mix:

- read-only retrieval
- notifications
- file reads
- browser actions
- sandbox execution
- direct shell execution

These need formal permission classes in Phase 6.

### 5. Host integrations are scattered

Desktop notifications, audio stack, CLI bridges, shell execution, and capture tools are spread across different modules without one explicit host-integration layer.

---

## Recommended Next Boundary Decisions

These are the immediate architecture decisions Phase 6 should make next:

1. Freeze the API as transport/control plane, not as the permanent owner of identity logic.
2. Extract a real `IdentityManager` module from `src/api/main.py`.
3. Define a formal message contract between voice daemon and API.
4. Define planner states and execution traces as structured runtime entities.
5. Define tool safety classes and execution policy boundaries.

These items directly feed Task `6.1.2`.

