# Ingestion Flow

This document outlines the step-by-step order of the data ingestion pipeline and identifies potential failure points.

## Step Order

1. **Watch**: `src/ingestion/watcher.py` uses the `watchdog` library to monitor filesystem events (Create/Modify) in configured vault folders.
2. **Debounce**: A 2-second cooldown is applied to ensure a file is fully written before processing begins.
3. **Queue**: Validated file paths (.pdf, .md, .txt, .docx) are added to an in-memory processing queue.
4. **Hash Check**: SHA-256 hash is computed. If the hash exists in `ingestion_index.db`, the file is skipped to avoid redundant work.
5. **Extract**: `src/ingestion/pdf_extractor.py` (via `pymupdf`) extracts raw text, page numbers, and document metadata.
6. **Chunk**: `src/ingestion/chunker.py` applies a recursive + structural strategy to split text into 400–512 token chunks with 15% overlap.
7. **Embed**: `src/ingestion/embedder.py` generates 768-dimensional vectors using `nomic-embed-text` via Ollama.
8. **Store**: `src/ingestion/vector_store.py` inserts chunks, vectors, and metadata into the appropriate LanceDB table.

## Potential Failure Points

| Step | Failure Mode | Mitigation |
|---|---|---|
| **Watch** | Missed events due to OS inotify limits. | Fallback to periodic polling if necessary. |
| **Debounce** | Processing starts too early on large files. | Increase debounce timer for specific extensions. |
| **Extract** | Scanned PDFs return empty text. | Detect empty pages and flag for Tesseract OCR. |
| **Chunk** | Lost context at boundaries. | Use overlapping windows (15-20%). |
| **Embed** | Ollama service is unreachable or slow. | Exponential backoff and retry logic. |
| **Store** | LanceDB index corruption on crash. | Use Lance's versioning for safe rollbacks. |
