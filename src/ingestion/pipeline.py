# MODULE: Ingestion pipeline that watches files, extracts content, chunks text, embeds vectors, and stores results.
"""Coordinate file ingestion from disk into retrieval storage."""

from __future__ import annotations

import threading
import time
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue

from config import VAULT_DIR
from src.common.file_types import ALLOWED_EXTENSIONS, get_file_type_label, is_allowed_file
from src.common.logging_utils import configure_logging
from src.common.text_normalization import full_normalization
from src.ingestion.chunker import Chunker
from src.ingestion.embedder import Embedder
from src.ingestion.pdf_extractor import ExtractedPage, PDFExtractor
from src.ingestion.state import IngestionStateStore, compute_file_hash
from src.ingestion.vector_store import VectorStore
from src.ingestion.watcher import FileWatcher

try:
    from docx import Document
except ImportError:  # pragma: no cover - optional dependency at runtime until env is fixed
    Document = None


class IngestionPipeline:
    """Run the end-to-end ingestion workflow for supported local files."""

    def __init__(self) -> None:
        """Initialize pipeline components and shared runtime state."""
        self.logger = configure_logging(__name__)
        self.queue: Queue = Queue()
        self.watcher = FileWatcher(queue=self.queue)
        self.extractor = PDFExtractor()
        self.chunker = Chunker()
        self.embedder = Embedder()
        self.documents_store = VectorStore("documents", embedder=self.embedder)
        self.personal_store = VectorStore("personal", embedder=self.embedder)
        self.state_store = IngestionStateStore()
        self._worker_thread: threading.Thread | None = None
        self._watcher_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start the watcher and background queue worker."""
        if self._worker_thread and self._worker_thread.is_alive():
            return

        self._stop_event.clear()
        self.ingest_directory(VAULT_DIR)

        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

        self._watcher_thread = threading.Thread(target=self.watcher.start, daemon=True)
        self._watcher_thread.start()

        self.logger.info("Ingestion pipeline started.")

    def stop(self) -> None:
        """Stop the watcher and background worker."""
        self._stop_event.set()
        self.watcher.stop()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
        if self._watcher_thread and self._watcher_thread.is_alive():
            self._watcher_thread.join(timeout=2.0)
        self.logger.info("Ingestion pipeline stopped.")

    def ingest_file(self, filepath: Path) -> dict:
        """Ingest one supported file into the appropriate vector store.

        Parameters:
            filepath: File to ingest.

        Returns:
            dict: Ingestion statistics including chunk count and elapsed time.
        """
        started = time.perf_counter()
        if not is_allowed_file(filepath):
            raise ValueError(f"Unsupported file type: {filepath}")
        if not filepath.exists():
            raise FileNotFoundError(filepath)

        file_hash = compute_file_hash(filepath)
        if self.state_store.has_hash(file_hash):
            return {"status": "skipped", "reason": "already_ingested", "chunks": 0, "file": str(filepath)}

        pages = self._extract_pages(filepath)
        if not pages:
            return {"status": "skipped", "reason": "no_extractable_content", "chunks": 0, "file": str(filepath)}

        chunks = self.chunker.chunk(pages, filepath)
        if not chunks:
            return {"status": "skipped", "reason": "no_chunks", "chunks": 0, "file": str(filepath)}

        vectors = self.embedder.embed_batch([chunk.text for chunk in chunks])
        if len(vectors) != len(chunks):
            raise RuntimeError("Embedding count mismatch during ingestion.")

        documents_chunks: list = []
        documents_vectors: list[list[float]] = []
        personal_chunks: list = []
        personal_vectors: list[list[float]] = []

        for chunk, vector in zip(chunks, vectors, strict=True):
            if self._is_private_chunk(chunk):
                personal_chunks.append(chunk)
                personal_vectors.append(vector)
            else:
                documents_chunks.append(chunk)
                documents_vectors.append(vector)

        if documents_chunks:
            self.documents_store.add(documents_chunks, documents_vectors)
        if personal_chunks:
            self.personal_store.add(personal_chunks, personal_vectors)

        self.state_store.record_file(filepath, file_hash)
        elapsed = time.perf_counter() - started
        self.logger.info("✅ %s: %d chunks ingested in %.1fs", filepath.name, len(chunks), elapsed)
        return {
            "status": "ok",
            "file": str(filepath),
            "chunks": len(chunks),
            "elapsed_seconds": round(elapsed, 3),
        }

    def ingest_directory(self, dirpath: Path) -> dict:
        """Bulk-ingest supported files from one directory tree.

        Parameters:
            dirpath: Root directory to scan recursively.

        Returns:
            dict: Summary statistics for the directory ingest.
        """
        processed = 0
        skipped = 0
        for filepath in dirpath.rglob("*"):
            if not filepath.is_file() or not is_allowed_file(filepath):
                continue
            try:
                result = self.ingest_file(filepath)
            except Exception as exc:
                skipped += 1
                self.logger.error("Bulk ingest failed for %s: %s", filepath, exc)
                self._append_error(filepath=filepath, error=exc)
                continue
            if result["status"] == "ok":
                processed += 1
            else:
                skipped += 1
        return {"processed": processed, "skipped": skipped, "directory": str(dirpath)}

    def status(self) -> dict:
        """Return a lightweight snapshot of current pipeline state.

        Returns:
            dict: Queue depth, watcher state, and vector-table counts when available.
        """
        return {
            "queue_size": self.queue.qsize(),
            "watcher_running": getattr(self.watcher, "_running", False),
            "documents_count": self.documents_store.count(),
            "personal_count": self.personal_store.count(),
        }

    def _process_queue(self) -> None:
        """Continuously process queued file paths until stopped."""
        while not self._stop_event.is_set():
            try:
                filepath = self.queue.get(timeout=0.5)
            except Empty:
                continue

            current_path = Path(filepath)
            try:
                self.ingest_file(current_path)
            except Exception as exc:
                self.logger.error("Failed to ingest %s: %s", filepath, exc)
                self._append_error(filepath=current_path, error=exc)
            finally:
                self.watcher.event_handler.clear_pending(current_path)
                self.queue.task_done()

    def _extract_pages(self, filepath: Path) -> list[ExtractedPage]:
        """Extract normalized page-like content from a supported file.

        Parameters:
            filepath: Source file path.

        Returns:
            list[ExtractedPage]: Extracted pages for downstream chunking.
        """
        suffix = filepath.suffix.lower()
        file_type = get_file_type_label(filepath)
        if file_type == "pdf":
            return self.extractor.extract(filepath)
        if file_type in {"markdown", "text"}:
            text = full_normalization(filepath.read_text(encoding="utf-8"))
            return [
                ExtractedPage(
                    text=text,
                    page_number=1,
                    source_file=str(filepath),
                    document_title=filepath.stem,
                    is_scanned=False,
                )
            ]
        if file_type == "word":
            if Document is None:
                self.logger.warning("python-docx unavailable; DOCX skipped: %s", filepath)
                return []
            document = Document(filepath)
            text = full_normalization(
                "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
            )
            return [
                ExtractedPage(
                    text=text,
                    page_number=1,
                    source_file=str(filepath),
                    document_title=filepath.stem,
                    is_scanned=False,
                )
            ]
        raise ValueError(f"Unsupported file type: {filepath}")

    def _append_error(self, filepath: Path, error: Exception) -> None:
        """Append a simplified unresolved error entry to `ERRORS.md`.

        Parameters:
            filepath: File being processed when the error occurred.
            error: Exception raised during ingestion.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")
        with Path("ERRORS.md").open("a", encoding="utf-8") as handle:
            handle.write(
                "\n## ERROR AUTO-PIPELINE: Ingestion failure\n"
                f"- **Date:** {timestamp}\n"
                "- **Phase/Task:** Phase 1, Task 1.7\n"
                f"- **Operation:** ingest_file({filepath})\n"
                f"- **Error message:** {error}\n"
                "- **Root cause:** Pending investigation\n"
                "- **Fix applied:** None yet\n"
                "- **Status:** UNRESOLVED\n"
            )

    def _is_private_chunk(self, chunk) -> bool:
        """Return whether a chunk must stay in the private local table.

        Parameters:
            chunk: Chunk-like object with a `domain` field.

        Returns:
            bool: True for personal or religious content.
        """
        return chunk.domain in {"personal", "religion"}


def main() -> None:
    """Start the ingestion pipeline and keep the watcher running."""
    pipeline = IngestionPipeline()
    pipeline.start()
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        pipeline.stop()
