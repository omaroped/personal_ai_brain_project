# Personal AI Brain: Master Engineering Plan v5.0

## 1. Vision: The Digital Brain Partner
To bridge the human-machine cognitive gap by synthesizing local-first data storage with advanced cognitive memory, real-time voice synthesis, and desktop-use agent frameworks.

## 2. Project Constitution (CLAUDE.md)
The project is governed by a strict set of rules for AI agents to prevent drift, context loss, and scope creep.
* **Source of Truth:** `CLAUDE.md` and `STATUS.md`.
* **Workflow:** Specify (specs/) -> Plan -> Implement (src/) -> Validate (tests/).

## 3. Technology Stack (Locked)
* **Runtime:** Python 3.11
* **Memory:** Letta (MemGPT) + LanceDB + pgvector
* **Inference:** Ollama (Mistral-7B / Llama-3)
* **Voice:** Whisper.cpp (STT) + Kokoro ONNX (TTS)
* **Agency:** Agent S + Bytebot (Docker Sandbox)

## 4. Implementation Roadmap

### Phase 1 — The Vault (Weeks 1-2)
* **Goal:** A searchable local knowledge base.
* **Key Tasks:** File watcher, semantic indexing (LanceDB), Query CLI.

### Phase 2 — The Memory Engine (Weeks 3-4)
* **Goal:** Stateful continuity and user profiling.
* **Key Tasks:** Letta integration, User Profile extraction, Daily Review cycle.

### Phase 3 — Ingestion Pipelines (Weeks 5-6)
* **Goal:** Automated brain growth.
* **Key Tasks:** Browser bookmarklet, PDF auto-processor, YouTube fetcher.

### Phase 4 — The Voice Layer (Week 7)
* **Goal:** 1.4s latency natural voice interaction.
* **Key Tasks:** Whisper.cpp (GPU), Kokoro ONNX, hotkey trigger.

### Phase 5 — Agency & Proactivity (Week 8+)
* **Goal:** Autonomous "Computer-Use" and proactive assistance.
* **Key Tasks:** Bytebot Sandbox, Task Planner, Proactive Side-panel.

## 5. Security & Safety
* **Sandbox:** All script executions and web browsing occur in a Docker container.
* **Permission:** Human-in-the-loop "Dry Run" for any host file manipulation.
* **Privacy:** Local-first by default; workspace isolation for sensitive data.

---
*Last Updated: June 5, 2026*
