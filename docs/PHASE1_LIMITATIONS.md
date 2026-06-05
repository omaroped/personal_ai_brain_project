# MODULE: Phase 1 Limitations and Known Blockers

This document lists the known runtime blockers, incomplete validations, and inherent technical limitations identified during Phase 1 (The Vault) implementation.

## 1. Runtime Blockers

### 1.1 Python Environment Instability
- **Status:** BLOCKED
- **Issue:** The checked-in virtual environment (`venv/`) points to an inaccessible Python 3.11 runtime. The host system's `python3` does not provide necessary tools like `venv`, `pip`, or `pytest`.
- **Impact:** End-to-end validation of the ingestion pipeline and CLI tools is currently impossible in the local shell. Code implementation is proceeding based on static analysis and unit-level assumptions.

## 2. Extraction & Ingestion Limitations

### 2.1 Arabic Text Extraction (OCR vs. Digital)
- **Issue:** While `pymupdf` is used for high-speed extraction, some Arabic PDFs use non-standard encodings that result in garbled text.
- **Limitation:** The current fallback to `pytesseract` (OCR) is significantly slower and requires specific system dependencies (`tesseract-ocr-ara`).
- **Current Mitigation:** Using `rawdict` extraction to capture Unicode points, but complex RTL (Right-to-Left) rendering issues remain a risk for certain document types.

### 2.2 LanceDB Concurrency
- **Issue:** LanceDB does not natively support multiple concurrent writers from different Python processes.
- **Limitation:** If the file watcher and a manual CLI ingestion command attempt to write to the same table simultaneously, data corruption may occur.
- **Requirement:** Mandatory use of file-based locking (`fasteners` library) for all write operations.

### 2.3 Watchdog Event Duplication
- **Issue:** OS-level file events (inotify) often fire multiple times for a single "save" operation (e.g., temp file write followed by rename).
- **Limitation:** Without debouncing, the pipeline would attempt to ingest the same file multiple times in rapid succession.
- **Mitigation:** A hardcoded 2-second debounce window is required for all watcher events.

## 3. Incomplete Live Validations

### 3.1 Ollama Cold-Start
- **Issue:** Ollama loads models into VRAM lazily. The first embedding request after a period of inactivity can take 2-8 seconds.
- **Validation:** Live health checks must include a "warmup" request to ensure the `nomic-embed-text` model is ready before the ingestion pipeline starts processing batches.

### 3.2 Letta Persistence
- **Issue:** Letta runs in Docker. Persistence is dependent on correct volume mounting of the PostgreSQL database.
- **Validation:** Automated checks for the existence of the `brain_project_starter_letta_data` volume are not yet integrated into the main health check script.

## 4. Hardware Constraints (RTX 3060 6GB)

- **Total VRAM Budget:** 5.5GB (out of 6GB total).
- **Concurrent Models:** Loading `mistral` (4.1GB) and `nomic-embed-text` (500MB) simultaneously with `faster-whisper` (600MB) leaves only ~300MB of headroom.
- **Risk:** High-resolution PDF extraction or large batch embedding runs may exceed VRAM limits if not carefully managed.
