# Personal AI Brain: Master Plan (v4.0) - The Self-Evolving Digital Twin

## 1. Vision: The Digital Brain Partner
To build a "Personalized AI Operating System" that acts as a digital extension of the human brain. It must be a **partner** that is aware of the user's history, mistakes, and future goals, operating as a "Personal OS" rather than a mere chat interface.

### Core Principles (Integrated 2026)
* **LLM as OS:** The agent acts as a kernel managing memory, state, and tools (Letta/MemGPT).
* **Frictionless Ingestion:** Zero-effort data capture from web, files, and system activity.
* **Hybrid Intelligence:** Local-first for privacy (Religious/Psychological data), Cloud-augmented for deep reasoning.
* **Reflective Growth:** Daily background "Sleep-Time Compute" cycles and active "Daily Reviews" for learning consolidation.

## 2. Technical Architecture
### A. The Memory Engine (Cognitive Tiering)
* **Management:** **Letta** for stateful runtime. Memory "paging" between Core (Active Context), Recall (Episodic), and Archival (Library).
* **Data Layer:** PostgreSQL + `pgvector` for episodic logs; LanceDB for local markdown/PDF indexing.
* **Self-Refinement:** Background cycles to prune contradictions and compress logs into episodic summaries.

### B. The Sensory & Ingestion Layer
* **Voice-First Loop:** Silero VAD -> Whisper.cpp -> Ollama/Llama -> Kokoro ONNX (1.4s latency).
* **Auto-Ingestion:** Browser extensions (Nexus-style), file watchers, and webhooks for YouTube/Notion/Gmail.

### C. The Action Layer (Desktop Agency)
* **Framework:** **Agent S** for planning + specialized "App Agents" for OS-level execution.
* **Security:** Sandboxed Ubuntu containers (**Bytebot**) for executing scripts and browsing.
* **Permissions:** Human-in-the-loop "Dry Run" mode for destructive actions.

## 3. Implementation Roadmap
* **Phase 1: Foundation (Weeks 1-2)**
    * Obsidian vault + AnythingLLM for basic RAG.
    * Setting up the `/opinions/` tracking system (Done).
* **Phase 2: Memory & Identity (Weeks 3-4)**
    * Integrating Letta for Core Memory management.
    * Establishing the "Daily Review" and "User Profile" extraction logic.
* **Phase 3: The Voice & Ingestion Loop (Weeks 5-6)**
    * Deploying the local STT/TTS pipeline and the Nexus-style capture tools.
* **Phase 4: Agentic Agency & Proactivity (Weeks 7-8)**
    * Bytebot sandbox setup and proactive side-panel for contextual help.

## 4. Business & Impact Strategy
* **Product Wedge:** "Academic/Professional Cognitive Partner" focusing on high-retention learning.
* **Privacy Edge:** 100% local embedding and workspace isolation for personal domains.

## 5. Metadata Tracking & Opinion Archive
See `/opinions/` for granular technical specs:
* `structured_integration.md` (Workflow)
* `cognitive_memory_tiers.md` (10/10) - *MemGPT Paradigm*
* `personal_os_paradigm.md` (10/10) - *LLM as OS*
* `local_voice_pipeline.md` (9/10) - *1.4s Latency*
* `desktop_orchestration.md` (9/10) - *Bytebot Sandbox*
* `ingestion_pipelines.md` (9/10) - *Nexus Capture*
* `hybrid_privacy_strategy.md` (9/10) - *Workspace Isolation*
* `proactive_synthesis.md` (8/10) - *Context Hygiene*
* `daily_log_reflection.md` (8/10) - *Nightly Review*

---
*Last Updated: June 5, 2026*
