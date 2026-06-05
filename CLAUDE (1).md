# CLAUDE.md — Personal AI Brain Project Constitution
# READ THIS ENTIRE FILE BEFORE DOING ANYTHING ELSE.

---

## 0. MANDATORY FIRST STEPS (every single session)

Before writing any code, running any command, or installing anything:

1. Read `STATUS.md` — find the exact task to resume
2. Read the spec file listed in STATUS.md under "Active Spec"
3. Tell the user:
   - What phase you are in
   - What the next uncompleted task is
   - What files you will touch
   - What you will NOT touch
4. Wait for user confirmation before proceeding

If STATUS.md says a task is "blocked", explain the blocker to the user and ask how to proceed.
Do NOT invent a workaround silently.

---

## 1. Project Identity

**Project:** Personal AI Brain (Second Brain / Digital Twin)
**Owner:** Omar
**Machine:** Ubuntu 22.04 LTS, Ryzen 5 5600H, RTX 3060 Laptop 6GB VRAM, 22GB RAM
**Project Root:** `/home/omar/personal_ai_brain_project/`
**Python version:** 3.11 (use `python3.11` explicitly in all commands)
**Virtual environment:** Always activate before any pip or python command:
  `source /home/omar/personal_ai_brain_project/venv/bin/activate`

---

## 2. Hard Rules (never break these)

### Code rules
- Every function must have a docstring explaining what it does, its parameters, and return value
- Every module must have a `# MODULE: description` comment at the top
- Use type hints everywhere: `def transcribe(audio_path: str) -> str:`
- No `print()` for logging — use the `logging` module at INFO level
- No bare `except:` — always catch specific exceptions: `except FileNotFoundError as e:`
- No hardcoded paths — use `config.py` constants or environment variables
- All secrets (API keys) go in `.env` file, loaded via `python-dotenv`. Never in code.

### Session rules
- After completing ANY task, update STATUS.md immediately (before moving to the next task)
- After hitting an error you cannot fix in 3 attempts: write to ERRORS.md and STOP
- Never install a library not listed in the current phase's spec file
- Never touch files outside the current phase's defined scope
- Run tests before marking any task done — no exceptions

### Privacy rules (CRITICAL)
- Data tagged with domain `personal` or `religion` MUST NEVER be sent to any cloud API
- This is enforced in `src/api/privacy_router.py` — never bypass this file's logic
- When in doubt about whether data is private: treat it as private

---

## 3. Tech Stack (locked — do not upgrade without checking compatibility)

| Component | Library | Version | Purpose |
|---|---|---|---|
| STT | faster-whisper | 1.1.0 | Speech to text, CUDA-optimized for NVIDIA |
| TTS | kokoro-onnx | 0.4.x | Text to speech, streaming, CPU-only |
| VAD | silero-vad | 5.1.x | Voice activity detection |
| Vector DB | lancedb | 0.8.x | Local vector store, file-based |
| Memory | letta-client | 0.2.x | Stateful agent memory (MemGPT paradigm) |
| PDF parsing | pymupdf | 1.24.x | Fast, handles Arabic, no server needed |
| File watch | watchdog | 4.0.x | OS-level inotify on Linux |
| API layer | fastapi | 0.111.x | Local HTTP endpoints |
| Embeddings | ollama (nomic-embed-text) | latest | Local, 768-dim, privacy-safe |
| LLM local | ollama (mistral) | latest | Fits in 5.5GB VRAM |
| LLM cloud | anthropic (claude-sonnet-4-20250514) | latest | Complex synthesis only |
| Torch | torch | 2.3.x | Required for Silero VAD |
| Env vars | python-dotenv | latest | Load .env secrets |

**Ollama must be running before any voice or embedding code is tested.**
Check: `curl http://localhost:11434/api/tags`

**Letta runs in Docker.** Start it with: `docker compose -f docker/docker-compose.yml up -d`
Check: `curl http://localhost:8283/health`

---

## 4. Project File Map

```
/home/omar/personal_ai_brain_project/
│
├── CLAUDE.md              ← this file (agent reads every session)
├── STATUS.md              ← current phase and task (agent reads every session)
├── ERRORS.md              ← known errors and fixes (agent reads every session)
├── requirements.txt       ← pinned dependencies
├── .env                   ← secrets (never commit)
├── .env.example           ← template showing required vars (safe to commit)
├── config.py              ← all path constants and settings
│
├── specs/                 ← one spec per phase, agent reads before coding
│   ├── phase1_vault.md
│   ├── phase2_memory.md
│   ├── phase3_ingestion.md
│   ├── phase4_voice.md
│   └── phase5_agency.md
│
├── src/
│   ├── memory/            ← Letta integration, core memory management
│   ├── ingestion/         ← file watcher, PDF parser, chunker, embedder
│   ├── voice/             ← STT, TTS, VAD pipeline
│   ├── agents/            ← planner agent, sub-agents
│   └── api/               ← FastAPI endpoints, privacy router
│
├── data/
│   ├── vault/             ← Obsidian-compatible markdown notes
│   ├── vectordb/
│   │   ├── documents/     ← public knowledge (books, articles, lectures)
│   │   ├── personal/      ← PRIVATE — never cloud API
│   │   ├── conversations/ ← compressed past sessions
│   │   └── errors/        ← mistake tracker
│   └── logs/              ← daily review logs (YYYY-MM-DD.md)
│
├── docker/
│   └── docker-compose.yml ← Letta + PostgreSQL
│
└── tests/
    ├── test_phase1.py
    ├── test_phase2.py
    └── ...
```

---

## 5. VRAM Budget (RTX 3060 Laptop, 6GB)

| Service | VRAM Usage | Notes |
|---|---|---|
| faster-whisper base | ~600MB | Load once, keep warm |
| Ollama mistral-7b (Q4) | ~4.1GB | Main LLM |
| nomic-embed-text | ~500MB | Embedding model |
| Silero VAD | ~0MB | CPU only |
| Kokoro ONNX TTS | ~0MB | CPU only |
| **Total** | **~5.2GB** | 0.8GB headroom |

**Do not load any model that pushes total VRAM above 5.5GB.**
If an operation requires more VRAM temporarily, unload one model first.

---

## 6. Error Handling Pattern (use everywhere)

```python
import logging
import time

MAX_RETRIES = 3
logger = logging.getLogger(__name__)

for attempt in range(MAX_RETRIES):
    try:
        result = risky_operation()
        break
    except SpecificException as e:
        logger.warning(f"Attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
        if attempt == MAX_RETRIES - 1:
            # Write to ERRORS.md and stop
            with open("ERRORS.md", "a") as f:
                f.write(f"\n## ERROR: {datetime.now()}\n- Operation: risky_operation\n- Error: {e}\n- Status: UNRESOLVED\n")
            raise
        time.sleep(2 ** attempt)  # exponential backoff: 1s, 2s, 4s
```

---

## 7. How to Run Tests

```bash
# Activate venv first
source /home/omar/personal_ai_brain_project/venv/bin/activate

# Run all tests for current phase
pytest tests/test_phase1.py -v

# Run a specific test
pytest tests/test_phase1.py::test_file_watcher_detects_new_pdf -v

# A task is NOT done until all its tests pass
```

---

## 8. Definition of "Task Complete"

A task is complete when ALL of these are true:
- [ ] Code is written with docstrings and type hints
- [ ] All tests for that task pass (`pytest -v`)
- [ ] No new entries in ERRORS.md from this task
- [ ] STATUS.md is updated to mark the task done
- [ ] If the task creates a new file, that file has a `# MODULE:` header comment

---

## 9. When You Are Stuck

If you cannot solve an error after 3 attempts:
1. Write the error to ERRORS.md with full traceback
2. Write what you tried (all 3 attempts)
3. Mark the task as BLOCKED in STATUS.md
4. Tell the user exactly: "I am stuck on [task]. The error is [X]. I tried [Y]. I need your decision on [Z]."
5. Stop. Do not attempt a 4th workaround.

This is not a failure. This is the correct behaviour.

---

## 10. Starting the First Session (Phase 1, Task 1)

If this is the very first session and nothing exists yet:

```bash
# 1. Create virtual environment
cd /home/omar/personal_ai_brain_project
python3.11 -m venv venv
source venv/bin/activate

# 2. Install base dependencies
pip install -r requirements.txt

# 3. Start Letta (needed from Phase 2 onward, start now so it's indexed)
docker compose -f docker/docker-compose.yml up -d

# 4. Verify Ollama is running
curl http://localhost:11434/api/tags

# 5. Pull required models
ollama pull mistral
ollama pull nomic-embed-text

# 6. Begin Phase 1, Task 1 (see specs/phase1_vault.md)
```
