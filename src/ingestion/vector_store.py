# MODULE: LanceDB-backed vector store with safe writes, hybrid search, and search result shaping.
"""Store and retrieve retrieval chunks using LanceDB."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import fasteners
import lancedb
import pyarrow as pa

from config import EMBED_DIMENSIONS, VECTORDB_DIR, ensure_directories
from src.ingestion.chunker import Chunk
from src.ingestion.embedder import Embedder
from src.ingestion.state import compute_file_hash

LANCEDB_SCHEMA = pa.schema(
    [
        pa.field("id", pa.string()),
        pa.field("text", pa.string()),
        pa.field("display_text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), EMBED_DIMENSIONS)),
        pa.field("source_file", pa.string()),
        pa.field("page_number", pa.int32()),
        pa.field("section", pa.string()),
        pa.field("chunk_index", pa.int32()),
        pa.field("domain", pa.string()),
        pa.field("content_type", pa.string()),
        pa.field("file_hash", pa.string()),
        pa.field("created_at", pa.string()),
    ]
)

VECTOR_SCHEMA = LANCEDB_SCHEMA


@dataclass
class SearchResult:
    """Represents one search hit returned from the vector store.

    Parameters:
        text: Clean chunk text.
        display_text: Human-readable chunk with source header.
        source_file: Source document path.
        page_number: One-based page number from the source.
        section: Source section heading.
        domain: Detected chunk domain.
        score: Search relevance score.
    """

    text: str
    display_text: str
    source_file: str
    page_number: int
    section: str
    domain: str
    score: float


class VectorStore:
    """Wrap LanceDB operations for chunk storage and retrieval."""

    def __init__(self, table_name: str, embedder: Embedder | None = None) -> None:
        """Initialize the vector store for one logical table.

        Parameters:
            table_name: Table name such as `documents` or `personal`.
            embedder: Optional shared embedder instance.
        """
        ensure_directories()
        self.table_name = table_name
        self.db = lancedb.connect(str(VECTORDB_DIR))
        self.lock = fasteners.InterProcessLock("/tmp/lancedb_write.lock")
        self.embedder = embedder
        self.table = self._open_or_create_table()

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Insert chunks and their vectors into the configured LanceDB table.

        Parameters:
            chunks: Chunk objects to store.
            vectors: Embedding vectors aligned with the chunks list.
        """
        if len(chunks) != len(vectors):
            raise ValueError("Chunks and vectors must have the same length.")

        records: list[dict] = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            source_path = Path(chunk.source_file)
            file_hash = compute_file_hash(source_path) if source_path.exists() else ""
            records.append(
                {
                    "id": str(uuid4()),
                    "text": chunk.text,
                    "display_text": chunk.display_text,
                    "vector": vector,
                    "source_file": chunk.source_file,
                    "page_number": chunk.page_number,
                    "section": chunk.section,
                    "chunk_index": chunk.chunk_index,
                    "domain": chunk.domain,
                    "content_type": chunk.content_type,
                    "file_hash": file_hash,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        if not records:
            return

        with self.lock:
            self.table.add(records)

    def search(
        self, query: str, top_k: int = 5, domain_filter: str | None = None
    ) -> list[SearchResult]:
        """Run vector search over the table and optionally filter by domain.

        Parameters:
            query: Query text to embed and search for.
            top_k: Maximum number of results to return.
            domain_filter: Optional domain label filter.

        Returns:
            list[SearchResult]: Search hits ordered by relevance.
        """
        if not query.strip():
            return []
        query_vector = self._get_embedder().embed(query)
        search_builder = self.table.search(query_vector)
        if domain_filter:
            search_builder = search_builder.where(f"domain = '{domain_filter}'")
        rows = search_builder.limit(top_k).to_list()
        return [self._to_search_result(row) for row in rows]

    def hybrid_search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Combine vector and keyword search using Reciprocal Rank Fusion.

        Parameters:
            query: Query text.
            top_k: Number of final hits to return.

        Returns:
            list[SearchResult]: Fused search hits.
        """
        if not query.strip():
            return []
        query_vector = self._get_embedder().embed(query)
        vector_results = self.table.search(query_vector).limit(top_k * 2).to_list()
        text_results = self.table.search(query, query_type="fts").limit(top_k * 2).to_list()
        merged = self._rrf_merge(vector_results, text_results, k=60)
        return [self._to_search_result(row) for row in merged[:top_k]]

    def count(self) -> int:
        """Return the number of stored rows in the table.

        Returns:
            int: Total table row count.
        """
        try:
            return int(self.table.count_rows())
        except Exception:
            return len(self.table.to_list())

    def already_ingested(self, file_hash: str) -> bool:
        """Check whether a file hash already exists in the table.

        Parameters:
            file_hash: SHA-256 hash of a source file.

        Returns:
            bool: True when the file hash is already stored.
        """
        if not file_hash:
            return False
        rows = self.table.search().where(f"file_hash = '{file_hash}'").limit(1).to_list()
        return bool(rows)

    def _open_or_create_table(self):
        """Open the configured table or create it with the canonical schema.

        Returns:
            Any: LanceDB table handle.
        """
        existing_tables = set(self.db.table_names())
        if self.table_name in existing_tables:
            return self.db.open_table(self.table_name)
        with self.lock:
            refreshed_tables = set(self.db.table_names())
            if self.table_name in refreshed_tables:
                return self.db.open_table(self.table_name)
            table = self.db.create_table(self.table_name, schema=LANCEDB_SCHEMA)
            try:
                table.create_fts_index("text", replace=True)
            except Exception:
                pass
            return table

    def _get_embedder(self) -> Embedder:
        """Return the shared embedder, creating it lazily when needed.

        Returns:
            Embedder: Embedder instance for query vector generation.
        """
        if self.embedder is None:
            self.embedder = Embedder()
        return self.embedder

    def _rrf_merge(self, list_a: list[dict], list_b: list[dict], k: int = 60) -> list[dict]:
        """Merge two ranked result lists using Reciprocal Rank Fusion.

        Parameters:
            list_a: First ranked result list.
            list_b: Second ranked result list.
            k: RRF smoothing constant.

        Returns:
            list[dict]: Merged result rows ordered by fused score.
        """
        scores: dict[str, float] = {}
        items_by_id: dict[str, dict] = {}

        for rank, item in enumerate(list_a):
            item_id = item["id"]
            items_by_id[item_id] = item
            scores[item_id] = scores.get(item_id, 0.0) + 1 / (k + rank + 1)

        for rank, item in enumerate(list_b):
            item_id = item["id"]
            items_by_id[item_id] = item
            scores[item_id] = scores.get(item_id, 0.0) + 1 / (k + rank + 1)

        sorted_ids = sorted(scores, key=scores.get, reverse=True)
        merged: list[dict] = []
        for item_id in sorted_ids:
            row = dict(items_by_id[item_id])
            row["_rrf_score"] = scores[item_id]
            merged.append(row)
        return merged

    def _to_search_result(self, row: dict) -> SearchResult:
        """Convert a LanceDB row into a typed search result.

        Parameters:
            row: Raw row returned from LanceDB.

        Returns:
            SearchResult: Typed search result.
        """
        score = self._score_from_row(row)
        return SearchResult(
            text=row["text"],
            display_text=row["display_text"],
            source_file=row["source_file"],
            page_number=int(row["page_number"]),
            section=row.get("section", "Unknown"),
            domain=row["domain"],
            score=score,
        )

    def _score_from_row(self, row: dict) -> float:
        """Normalize row scoring into a higher-is-better value.

        Parameters:
            row: Raw LanceDB row.

        Returns:
            float: Normalized relevance score.
        """
        if "_rrf_score" in row:
            return float(row["_rrf_score"])
        if "_distance" in row:
            distance = float(row["_distance"])
            return 1.0 / (1.0 + max(distance, 0.0))
        return 0.0


def default_table_paths() -> dict[str, Path]:
    """Return the default logical table paths used by the project.

    Returns:
        dict[str, Path]: Mapping of standard table names to on-disk paths.
    """
    return {
        "documents": VECTORDB_DIR / "documents",
        "personal": VECTORDB_DIR / "personal",
        "conversations": VECTORDB_DIR / "conversations",
        "errors": VECTORDB_DIR / "errors",
    }
