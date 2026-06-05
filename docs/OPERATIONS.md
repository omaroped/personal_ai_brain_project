# Operations Guide: Personal AI Brain

## Service Management

### 1. Ollama (LLM & Embeddings)
- **Check Status:** `curl http://localhost:11434/api/tags`
- **Models Required:** `mistral`, `nomic-embed-text`.
- **Startup:** Should start automatically as a service on Ubuntu. If not: `ollama serve`.

### 2. Letta (Memory Agent)
- **Check Status:** `curl http://localhost:8283/health`
- **Startup:** 
  ```bash
  cd docker
  docker compose up -d
  ```
- **Volume Persistence:** Data is stored in the `letta_data` named volume.

### 3. File Watcher
- **Check Status:** Check `data/logs/brain.log` for heartbeat messages.
- **Startup:** (Planned) `python -m src.ingestion.watcher`.

## Common Failures & Fixes

### "Shared library not found" when running python
- **Cause:** Broken virtual environment.
- **Fix:** Run `scripts/rebuild_venv.sh`.

### "Ollama connection refused"
- **Cause:** Ollama service is not running.
- **Fix:** Start Ollama or check `systemctl status ollama`.

### "Letta 500 Internal Server Error"
- **Cause:** PostgreSQL container within Docker may be out of sync or disk space is full.
- **Fix:** `docker compose restart` in the `docker/` folder.

## Logs
- **App Logs:** `data/logs/brain.log`
- **Audit Logs:** `data/logs/audit.log` (planned)
- **Error Tracking:** Check `ERRORS.md` in the project root.
