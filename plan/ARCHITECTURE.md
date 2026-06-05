# Project Architecture: Personal AI Brain

## 1. System Overview

The Personal AI Brain is a local-first, privacy-focused digital twin designed to synthesize a knowledge vault with stateful memory and a voice-first interface. It operates as a "Personal OS" where the LLM manages its own context and tools.

## 2. Core Components

### 2.1 Configuration (`config.py`)
- Central source of truth for paths, model labels, chunk sizes, and privacy domain blocks.
- Uses `python-dotenv` for local environment variable management.

### 2.2 Ingestion Subsystem (`src/ingestion/`)
- **File Watcher (`watcher.py`):** Monitors `Documents`, `Downloads`, and `data/vault` using the `watchdog` library. Implements a 2-second debounce to handle multi-stage file saves.
- **Ingestion State (`state.py`):** Uses SHA-256 file hashing and a SQLite database (`ingestion_index.db`) to ensure every file is processed exactly once.
- **Extractor (`pdf_extractor.py`):** Parses PDFs using `pymupdf`. Includes heuristic detection for scanned pages and an OCR fallback path (tesseract).
- **Chunker (`chunker.py`):** Implements a recursive-character hybrid strategy (512 tokens, 15% overlap). Injects structural context (Title, Section, Page) into the display text of each chunk.
- **Embedder (`embedder.py`):** Generates 768-dim vectors using `nomic-embed-text` via the local Ollama API. Includes a warmup routine to prevent first-call latency spikes.
- **Vector Store (`vector_store.py`):** LanceDB-backed storage. Implements **Hybrid Search** combining vector similarity and BM25 full-text search fused via Reciprocal Rank Fusion (RRF).

### 2.3 Memory Engine (`src/memory/`, Letta)
- **Core Memory:** High-priority active context (identity, goals, active domains) stored in `core_memory.json`.
- **Recall Memory:** Searchable PostgreSQL-backed conversation history managed by the Letta runtime.
- **Archival Memory:** The long-term knowledge vault stored in LanceDB, retrieved via the `search_archival` tool.
- **Daily Review:** Nightly consolidation process that extracts facts and mistakes into core memory.

### 2.4 Voice Layer (`src/voice/`)
- **STT:** `faster-whisper` (base model, CUDA-optimized) for low-latency transcription.
- **VAD:** `silero-vad` for real-time speech detection on CPU.
- **TTS:** `kokoro-onnx` for streaming, studio-quality speech synthesis on CPU.
- **Pipeline:** End-to-end loop with ~1.5s total latency target.

### 2.5 API & Routing (`src/api/`)
- **Privacy Router (`privacy_router.py`):** Enforces a "Privacy Shield" that blocks sensitive domains (`personal`, `religion`) from ever being sent to cloud-based reasoning models.

### 2.6 CLI & Interface (`query.py`)
- **Typer-based CLI:** Entry point for searching the vault, checking system health, and inspecting privacy routing decisions.

## 3. Data Flow

1. **Ingestion Flow:** `watcher` → `state.py` (hash check) → `pdf_extractor` → `chunker` → `embedder` → `vector_store`.
2. **Retrieval Flow:** `query.py` → `privacy_router` → `vector_store` (Hybrid Search) → `LLM Synthesis`.
3. **Voice Flow:** `VAD` → `STT` → `Letta Agent` → `TTS Streaming`.

## 4. Storage & Persistence

| Data Type | Technology | Path |
|---|---|---|
| Vector Knowledge | LanceDB | `data/vectordb/` |
| Agent State | Letta (PostgreSQL) | Docker Volume |
| Ingestion Index | SQLite | `data/ingestion_index.db` |
| Raw Vault | Markdown/PDF | `data/vault/` |
| Daily Logs | Markdown | `data/logs/` |

## 5. Architecture Decision Records (ADR)

- **ADR 01: Hybrid Search:** Use BM25 + Vector with Reciprocal Rank Fusion (RRF) for high-precision retrieval of specific terms and semantic concepts.
- **ADR 02: Letta for Memory:** Adopt the MemGPT paradigm to allow the agent to manage its own long-term state via tool calls.
- **ADR 03: Local-First STT/TTS:** Prioritize CPU/GPU local models over cloud APIs to ensure offline availability and total privacy.
- **ADR 04: LanceDB for Vector Storage:** Choose LanceDB for its version-safe storage format and ability to handle datasets larger than RAM.

## 6. Source of Truth Hierarchy

1. `CLAUDE.md` (Runtime rules)
2. `STATUS.md` (Active task state)
3. `plan/ARCHITECTURE.md` (System design)
4. `ERRORS.md` (Learned corrections)
