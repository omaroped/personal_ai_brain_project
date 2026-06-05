# Phase 1 Spec: The Vault (v5.1 Deep)

## Goal
Build the data foundation: A recursive, semantic, local-first RAG knowledge base.

## 1. File Watcher (`watchdog`)
- **Folders:** `~/Documents`, `~/Downloads`, `data/vault`.
- **Logic:** Debounce (2s delay), SQLite-backed deduplication (hash-based).
- **Types:** .pdf, .md, .txt, .docx.

## 2. Extraction & Chunking (`pymupdf`)
- **Strategy:** Recursive Character Splitter (512 tokens, 15% overlap).
- **Context Injection:** Prepend Doc title + Section + Page to metadata.
- **OCR Fallback:** Use `pytesseract` (ara+eng) if page is image-only.
- **Auto-Tagging:** Keyword-based domain classification (Psychology, Religion, etc.).

## 3. Vector Database (`LanceDB`)
- **Embedding:** `nomic-embed-text` via Ollama (Local).
- **Hybrid Search:** Vector + BM25 (Full-Text Search) with Reciprocal Rank Fusion (RRF).
- **Privacy:** `personal` and `religion` tables never touch cloud APIs.

## Tasks
1. [ ] Setup Python 3.11 Environment & Requirements.
2. [ ] Implement File Watcher with Debounce logic.
3. [ ] Build PDF/MD Extractor with `pymupdf`.
4. [ ] Implement Recursive Chunking & Auto-Tagging.
5. [ ] Integrate LanceDB with Hybrid Search (Vector+FTS).
6. [ ] Build `query.py` CLI for validation.
