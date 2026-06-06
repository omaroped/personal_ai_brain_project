# MODULE: Persistent mistake tracking and lightweight relevance search for pre-task checks.
"""Machine-readable mistake tracking with duplicate merging and query helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import tempfile
import uuid

from src.common.logging_utils import configure_logging
from src.ingestion.vector_store import VectorStore

LOGGER = configure_logging(__name__)


def _atomic_write_json(path: Path, payload: list[dict]) -> None:
    """Write JSON data atomically to avoid partial corruption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    ) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


def _tokenize(text: str) -> set[str]:
    """Split simple lowercase word tokens for lightweight matching."""
    return {part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if part}


@dataclass
class MistakeTracker:
    """Store, deduplicate, and query mistakes with semantic vector search."""

    storage_path: Path
    vector_store: VectorStore | None = None

    def __post_init__(self):
        if self.vector_store is None:
            # Mistake tracker uses the 'errors' table in LanceDB
            self.vector_store = VectorStore("errors")

    def _load_all(self) -> list[dict]:
        if not self.storage_path.exists():
            return []
        payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Mistake tracker storage must contain a list")
        return payload

    def _save_all(self, records: list[dict]) -> None:
        _atomic_write_json(self.storage_path, records)

    def log_mistake(self, title: str, context: str, fix: str, tags: list[str]) -> None:
        """Store a mistake, merging duplicates by title and fix."""
        title_clean = title.strip()
        context_clean = context.strip()
        fix_clean = fix.strip()
        tags_clean = sorted({tag.strip().lower() for tag in tags if tag.strip()})

        records = self._load_all()
        for record in records:
            if (
                record["title"].strip().lower() == title_clean.lower()
                and record["fix"].strip().lower() == fix_clean.lower()
            ):
                record["context"] = context_clean or record["context"]
                record["tags"] = sorted(set(record.get("tags", [])) | set(tags_clean))
                record["last_seen_at"] = datetime.now(timezone.utc).isoformat()
                record["occurrences"] = int(record.get("occurrences", 1)) + 1
                self._save_all(records)
                LOGGER.info("Merged duplicate mistake record for %s", title_clean)
                return

        records.append(
            {
                "id": str(uuid.uuid4()),
                "title": title_clean,
                "context": context_clean,
                "fix": fix_clean,
                "tags": tags_clean,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_seen_at": datetime.now(timezone.utc).isoformat(),
                "occurrences": 1,
            }
        )

        # Add to vector store for semantic search
        if self.vector_store:
            self.vector_store.add_chunk(
                text=f"MISTAKE: {title_clean}\nCONTEXT: {context_clean}\nFIX: {fix_clean}",
                source_file=str(self.storage_path),
                section=title_clean,
                domain="mistake",
                metadata={"tags": tags_clean}
            )

        self._save_all(records)
        LOGGER.info("Logged new mistake record for %s", title_clean)

    def _fallback_search(self, query: str, limit: int = 5) -> list[dict]:
        """Return the most relevant prior mistakes for a query."""
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        scored: list[tuple[int, dict]] = []
        for record in self._load_all():
            haystack = " ".join(
                [
                    record.get("title", ""),
                    record.get("context", ""),
                    record.get("fix", ""),
                    " ".join(record.get("tags", [])),
                ]
            )
            score = len(query_tokens & _tokenize(haystack))
            if score > 0:
                scored.append((score, record))

        scored.sort(key=lambda item: (-item[0], -int(item[1].get("occurrences", 1))))
        return [record for _, record in scored[:limit]]

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Return the most relevant prior mistakes using semantic hybrid search."""
        if not hasattr(self, "vector_store") or not self.vector_store:
            return self._fallback_search(query, limit)

        try:
            results = self.vector_store.hybrid_search(query, top_k=limit)
            
            # Cross-reference vector results with full JSON records
            records = self._load_all()
            found_records = []
            
            for res in results:
                # Match by title/section
                for record in records:
                    if record["title"] == res.section:
                        if record not in found_records:
                            found_records.append(record)
                        break
            
            return found_records
        except Exception as exc:
            LOGGER.error("Vector search for mistakes failed: %s", exc)
            return self._fallback_search(query, limit)

    def pre_task_check(self, task_description: str) -> list[dict]:
        """Run a lightweight search before starting a task."""
        return self.search(task_description, limit=5)
