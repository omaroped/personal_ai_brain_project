# Project Status: Personal AI Brain

## Current Phase: Phase 1 — The Vault
**Goal:** A searchable local knowledge base you can actually query.

## Progress Tracker

### Phase 1: The Vault
- [x] Create the full project directory structure.
- [ ] Write a file watcher that monitors `~/Documents` and `data/vault` for new PDFs and markdown files.
- [ ] Implement chunking (512 tokens) and embedding (nomic-embed-text via Ollama) into LanceDB.
- [ ] Write `query.py` CLI for semantic search.
- [ ] Write tests and validate against actual PDFs.

### Phase 2: The Memory Engine
- [ ] Install and configure Letta with local Ollama backend.
- [ ] Create `core_memory.json` template (User Profile).
- [ ] Write `daily_review.py` script and integration.
- [ ] Implement extraction routine for log processing.
- [ ] Write "mistake tracker" memory namespace.

### Phase 3: Ingestion Pipelines
- [ ] Build browser bookmarklet for web capture.
- [ ] Develop FastAPI endpoint for content processing.
- [ ] Build automated PDF processor for `~/Documents`.
- [ ] Build YouTube transcript fetcher via `yt-dlp`.

### Phase 4: The Voice Layer
- [ ] Install and benchmark `whisper.cpp` on GPU.
- [ ] Install and benchmark `Kokoro ONNX`.
- [ ] Wire the `listen.py` pipeline (VAD/STT/LLM/TTS).
- [ ] Add hotkey trigger (Ctrl+Space).

### Phase 5: Agency & Proactivity
- [ ] Set up Bytebot Docker container.
- [ ] Build hierarchical task planner.
- [ ] Build proactive side panel (screen monitoring).
- [ ] Implement "Dry Run" / Human-in-the-loop permission model.

## Recent Updates
- **June 5, 2026:** Migrated to Master Engineering Plan v5.0. Established directory structure and project constitution (CLAUDE.md).
