# Vector Store Notes

Notes on the schema, search strategy, and ranking logic for the LanceDB vector store.

## Schema Definition

Each entry in the vector store follows this structured schema:

- `id`: UUID or unique hash of the chunk.
- `text`: The raw text content of the chunk.
- `vector`: 768-dimensional float array (`nomic-embed-text`).
- `source_file`: Absolute or relative path to the source document.
- `page_number`: 1-based index of the page where the text was found.
- `section`: The most recent heading or structural marker.
- `domain`: Content domain (e.g., `psychology`, `ai_tech`).
- `created_at`: ISO-8601 timestamp of ingestion.
- `chunk_index`: Sequence number within the original document.

## Full-Text Search (FTS)

While vector search captures semantic meaning, it can struggle with exact keyword matching for proper nouns, acronyms, or specific technical terms. We enable Full-Text Search (BM25) on the `text` column to ensure these terms remain discoverable.

## Hybrid Search and RRF

To achieve the best of both worlds, the system performs a hybrid search:
1. **Vector Search**: Finds the top K results by cosine similarity.
2. **FTS**: Finds the top K results by keyword relevance.
3. **Reciprocal Rank Fusion (RRF)**: Merges the two lists into a single ranked output.

**RRF Formula**:
`score = 1 / (k + rank_vector) + 1 / (k + rank_fts)`
*(where k is typically 60)*

This ensures that results appearing prominently in both searches are boosted to the top.
