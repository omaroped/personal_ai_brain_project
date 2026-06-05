# Phase 1 Spec: The Vault

## Goal
A searchable local knowledge base that indexes Markdown and PDF files using semantic search (RAG).

## Components
- **File Watcher:** Monitors `~/Documents` and `data/vault`.
- **Chamber (Indexer):** Chunks text, generates embeddings via Ollama (nomic-embed-text), and stores in LanceDB.
- **Query CLI:** A tool to search the knowledge base.

## Tasks
1. [x] Create directory structure.
2. [ ] Write file watcher script using `watchdog`.
3. [ ] Implement chunking (512 tokens, 50 overlap).
4. [ ] Integrate `nomic-embed-text` via Ollama API.
5. [ ] Store embeddings and metadata in local LanceDB.
6. [ ] Build `query.py` with top-5 retrieval and source attribution.

## Validation
- Querying for specific terms found in existing university PDFs returns accurate snippets.
