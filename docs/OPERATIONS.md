# Operations Guide: Personal AI Brain

## Core Local Services

| Service | Endpoint | Role | Check Command |
|---|---|---|---|
| **Ollama** | `http://localhost:11434` | LLM & Embeddings | `curl http://localhost:11434/api/tags` |
| **Letta** | `http://localhost:8283` | Agent Memory | `curl http://localhost:8283/health` |
| **FastAPI** | `http://localhost:8001` | Ingestion API | `curl http://localhost:8001/health` |

## Docker Management
The memory engine (Letta + PostgreSQL) runs via Docker Compose.

- **Start Services:**
  ```bash
  docker compose -f docker/docker-compose.yml up -d
  ```
- **Stop Services:**
  ```bash
  docker compose -f docker/docker-compose.yml down
  ```
- **View Logs:**
  ```bash
  docker compose -f docker/docker-compose.yml logs -f
  ```

## Log Locations
- **System Logs:** `data/logs/brain.log`
- **Inference Logs:** Output of the `src/ingestion/pipeline.py` process.
- **Docker Logs:** Captured by Docker stdout/stderr.

## Common Failure Modes

### 1. Ollama Model Not Loaded
- **Symptom:** Timeout errors (10s+) on the first ingestion or query.
- **Fix:** Send a warmup request or manually run `ollama run mistral` to preload the model into VRAM.

### 2. LanceDB Concurrent Write
- **Symptom:** "Table is locked" or index corruption.
- **Fix:** Ensure all writing processes use the `InterProcessLock` defined in `src/ingestion/vector_store.py`.

### 3. Letta Volume Persistence
- **Symptom:** Memory lost after Docker restart.
- **Fix:** Verify volume mount: `docker volume ls | grep letta`. If missing, check `docker-compose.yml` for correct volume naming.

### 4. GPU Memory Exhaustion
- **Symptom:** CUDA Out of Memory (OOM).
- **Fix:** Unload unused models from Ollama or reduce batch size in `src/ingestion/embedder.py`.
