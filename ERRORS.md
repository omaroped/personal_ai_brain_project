# ERRORS.md — Known Issues and Agent Mistakes Log
# The agent reads this at the start of every session.
# When a new error is found, append it at the bottom with the template below.

---

## HOW TO ADD AN ERROR

```
## ERROR [ID]: Short description
- **Date:** YYYY-MM-DD
- **Phase/Task:** e.g. Phase 1, Task 1.3
- **Operation:** What was being attempted
- **Error message:** (exact traceback or error text)
- **Root cause:** Why it happened
- **Fix applied:** Exact fix that worked
- **Status:** RESOLVED / UNRESOLVED / WORKAROUND APPLIED
```

---

## PRE-SEEDED KNOWN GOTCHAS
### (Read these before writing any code — they will save you hours)

---

## ERROR PRE-01: LanceDB concurrent write corruption
- **Phase/Task:** Phase 1, any write operation
- **Root cause:** LanceDB does not support multiple Python processes writing to the
  same table simultaneously. If the file watcher and a manual ingest run at the same time,
  the table can become corrupted.
- **Fix:** Use a file-based lock (`fasteners` library) before any LanceDB write.
  Only one writer at a time. Reads are safe to run concurrently.
- **Status:** RESOLVED (preventative — implement from the start)

```python
import fasteners
lock = fasteners.InterProcessLock('/tmp/lancedb_write.lock')
with lock:
    table.add(records)
```

---

## ERROR PRE-02: Ollama model not loaded when pipeline starts
- **Phase/Task:** Phase 1 Task 1.5 (embedder), Phase 4 (voice pipeline)
- **Root cause:** Ollama loads models lazily — the first call after restart takes 2-8
  seconds while the model loads into VRAM. This causes timeout errors in the pipeline.
- **Fix:** At application startup, send a warmup embedding request and wait for it to
  complete before marking the service as ready.
- **Status:** RESOLVED (preventative)

```python
def warmup_ollama():
    """Send a dummy request to ensure model is loaded before real requests arrive."""
    logger.info("Warming up Ollama embedding model...")
    ollama.embeddings(model="nomic-embed-text", prompt="warmup")
    logger.info("Ollama ready.")
```

---

## ERROR PRE-03: faster-whisper CUDA library not found
- **Phase/Task:** Phase 4, Task 4.1
- **Root cause:** faster-whisper requires `libcublas.so` which is in CUDA toolkit,
  not just CUDA drivers. Many Ubuntu setups have drivers but not the full toolkit.
- **Fix:** Install CUDA toolkit 12.x:
  ```bash
  sudo apt-get install cuda-toolkit-12-3
  ```
  Then verify: `python -c "import ctranslate2; print(ctranslate2.get_supported_compute_types('cuda'))"`
- **Status:** RESOLVED (preventative)

---

## ERROR PRE-04: pymupdf extracts garbled Arabic text
- **Phase/Task:** Phase 1, Task 1.3
- **Root cause:** Arabic PDFs sometimes use non-standard font encodings. pymupdf's
  default extraction reverses RTL text or misses diacritics (tashkeel).
- **Fix:** Use `page.get_text("rawdict")` and filter by `flags` for proper Unicode
  extraction. Then apply `arabic_reshaper` + `python-bidi` for display.
  ```bash
  pip install arabic-reshaper python-bidi
  ```
  For storage and embedding, the raw Unicode is fine — only reshaping needed for display.
- **Status:** RESOLVED (preventative)

---

## ERROR PRE-05: Watchdog fires duplicate events on file save
- **Phase/Task:** Phase 1, Task 1.2
- **Root cause:** Many text editors (VS Code, gedit) save files in two operations:
  write to temp file → rename to final. This fires TWO events for one save.
- **Fix:** Debounce all events with a 2-second window. Only process a file if no new
  events have arrived for that path in the last 2 seconds.
- **Status:** RESOLVED (preventative — built into watcher spec)

---

## ERROR PRE-06: Letta Docker container loses data on restart
- **Phase/Task:** Phase 2, setup
- **Root cause:** If the Docker volume is not correctly mounted, Letta's PostgreSQL
  database resets every time the container restarts.
- **Fix:** The docker-compose.yml already handles this with a named volume. Verify
  the volume exists after first start:
  ```bash
  docker volume ls | grep letta
  ```
  Expected output: `local    brain_project_starter_letta_data`
  If missing, the container will not persist memory.
- **Status:** RESOLVED (preventative — handled in docker-compose.yml)

---

## ERROR PRE-07: silero-vad model download fails in offline environments
- **Phase/Task:** Phase 4, Task 4.2
- **Root cause:** Silero VAD downloads its model from torch.hub on first use.
  If the machine has no internet at that moment, it fails silently.
- **Fix:** Pre-download the model explicitly in the setup step:
  ```bash
  python -c "import torch; torch.hub.load('snakers4/silero-vad', 'silero_vad', force_reload=True)"
  ```
  After this, the model is cached in `~/.cache/torch/hub/` and works offline.
- **Status:** RESOLVED (preventative)

---

## ERROR PRE-08: nomic-embed-text returns 768-dim but LanceDB schema expects different dim
- **Phase/Task:** Phase 1, Task 1.6
- **Root cause:** If you create a LanceDB table with the wrong vector dimension and
  then try to insert embeddings, you get a cryptic schema error. Very hard to debug.
- **Fix:** Always create the LanceDB table with explicit schema, never inferred:
  ```python
  import pyarrow as pa
  schema = pa.schema([
      pa.field("id", pa.string()),
      pa.field("text", pa.string()),
      pa.field("vector", pa.list_(pa.float32(), 768)),  # 768 for nomic-embed-text
      pa.field("source_file", pa.string()),
      pa.field("domain", pa.string()),
      pa.field("created_at", pa.string()),
  ])
  table = db.create_table("documents", schema=schema)
  ```
- **Status:** RESOLVED (preventative — use this schema template)

---

## ERROR PRE-09: FastAPI hangs when Ollama request is slow
- **Phase/Task:** Phase 3, Task 3.1
- **Root cause:** Synchronous Ollama calls inside an async FastAPI endpoint block
  the entire event loop, causing all requests to queue up.
- **Fix:** Always run Ollama calls in a thread pool executor:
  ```python
  import asyncio
  from concurrent.futures import ThreadPoolExecutor
  executor = ThreadPoolExecutor(max_workers=2)

  @app.post("/ingest/web")
  async def ingest_web(payload: WebPayload):
      loop = asyncio.get_event_loop()
      result = await loop.run_in_executor(executor, ollama_summarize, payload.text)
      return {"status": "ok"}
  ```
- **Status:** RESOLVED (preventative)

---

## ERROR PRE-10: Kokoro ONNX first-run downloads model weights
- **Phase/Task:** Phase 4, Task 4.4
- **Root cause:** On first run, Kokoro downloads ~300MB of model weights. This causes
  a 30-60 second delay that looks like a hang.
- **Fix:** Pre-download in the setup step:
  ```bash
  python -c "from kokoro_onnx import Kokoro; Kokoro('kokoro-v0_19.onnx', 'voices.bin')"
  ```
  After this, all subsequent runs are instant.
- **Status:** RESOLVED (preventative)

---

## AGENT-ADDED ERRORS GO BELOW THIS LINE

(Agent appends new errors here as they are discovered during development)
