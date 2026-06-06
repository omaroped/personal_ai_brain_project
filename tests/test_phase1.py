# MODULE: Phase 1 tests for watcher, extraction, chunking, embedding, storage, and pipeline behavior.
"""Phase 1 tests for the vault ingestion foundation."""

from __future__ import annotations

from pathlib import Path
from queue import Queue

from src.ingestion.chunker import Chunker
from src.ingestion.chunker import Chunk
from src.ingestion.embedder import Embedder
from src.ingestion.pipeline import IngestionPipeline
from src.ingestion.pdf_extractor import PDFExtractor
from src.ingestion.pdf_extractor import ExtractedPage
from src.ingestion.state import IngestionStateStore, compute_file_hash
from src.ingestion.vector_store import VectorStore
from src.ingestion.watcher import DEBOUNCE_SECONDS, IngestionEventHandler


class FakeFileEvent:
    """Simple file event stub for watcher tests."""

    def __init__(self, path: Path, is_directory: bool = False) -> None:
        """Build a minimal watchdog-compatible event stub.

        Parameters:
            path: File path represented by the event.
            is_directory: Whether the event points to a directory.
        """
        self.src_path = str(path)
        self.is_directory = is_directory


def test_watcher_accepts_supported_file_type(tmp_path: Path) -> None:
    """Supported file types should be queued when first seen."""
    queue: Queue = Queue()
    db_path = tmp_path / "ingestion_index.db"
    state_store = IngestionStateStore(db_path=db_path)
    handler = IngestionEventHandler(queue=queue, state_store=state_store)
    file_path = tmp_path / "note.md"
    file_path.write_text("# note", encoding="utf-8")

    handler.on_created(FakeFileEvent(file_path))

    queued = queue.get_nowait()
    assert queued == file_path


def test_watcher_skips_duplicate_hash_in_state_store(tmp_path: Path) -> None:
    """Previously ingested files should not be queued again."""
    queue: Queue = Queue()
    db_path = tmp_path / "ingestion_index.db"
    state_store = IngestionStateStore(db_path=db_path)
    handler = IngestionEventHandler(queue=queue, state_store=state_store)
    file_path = tmp_path / "paper.txt"
    file_path.write_text("already ingested", encoding="utf-8")
    file_hash = compute_file_hash(file_path)
    state_store.record_file(file_path, file_hash)

    handler.on_created(FakeFileEvent(file_path))

    assert queue.empty() is True


def test_watcher_debounces_repeat_events(tmp_path: Path) -> None:
    """Immediate repeated events for the same file should be ignored."""
    queue: Queue = Queue()
    db_path = tmp_path / "ingestion_index.db"
    state_store = IngestionStateStore(db_path=db_path)
    handler = IngestionEventHandler(queue=queue, state_store=state_store)
    file_path = tmp_path / "paper.md"
    file_path.write_text("new content", encoding="utf-8")

    handler.on_created(FakeFileEvent(file_path))
    handler.on_modified(FakeFileEvent(file_path))

    assert queue.qsize() == 1


def test_watcher_rejects_unsupported_extension(tmp_path: Path) -> None:
    """Unsupported file types should not be queued."""
    queue: Queue = Queue()
    db_path = tmp_path / "ingestion_index.db"
    state_store = IngestionStateStore(db_path=db_path)
    handler = IngestionEventHandler(queue=queue, state_store=state_store)
    file_path = tmp_path / "image.png"
    file_path.write_bytes(b"not supported")

    handler.on_created(FakeFileEvent(file_path))

    assert queue.empty() is True


def test_watcher_uses_shared_file_type_rules(tmp_path: Path) -> None:
    """Watcher should accept DOCX through the shared file-type helper."""
    queue: Queue = Queue()
    db_path = tmp_path / "ingestion_index.db"
    state_store = IngestionStateStore(db_path=db_path)
    handler = IngestionEventHandler(queue=queue, state_store=state_store)
    file_path = tmp_path / "outline.docx"
    file_path.write_bytes(b"docx placeholder")

    handler.on_created(FakeFileEvent(file_path))

    assert queue.get_nowait() == file_path


def test_debounce_allows_processing_after_threshold(tmp_path: Path) -> None:
    """The debounce helper should allow processing after the threshold passes."""
    queue: Queue = Queue()
    db_path = tmp_path / "ingestion_index.db"
    state_store = IngestionStateStore(db_path=db_path)
    handler = IngestionEventHandler(queue=queue, state_store=state_store)

    path = str(tmp_path / "future.md")
    assert handler._debounce(path) is True


def test_watcher_clear_pending_allows_future_requeue(tmp_path: Path) -> None:
    """Clearing a pending path should allow the same file to be queued again later."""
    queue: Queue = Queue()
    db_path = tmp_path / "ingestion_index.db"
    state_store = IngestionStateStore(db_path=db_path)
    handler = IngestionEventHandler(queue=queue, state_store=state_store)
    file_path = tmp_path / "paper.md"
    file_path.write_text("new content", encoding="utf-8")

    handler.on_created(FakeFileEvent(file_path))
    handler.clear_pending(file_path)
    handler._last_seen[str(file_path)] -= DEBOUNCE_SECONDS + 0.1
    handler.on_modified(FakeFileEvent(file_path))

    assert queue.qsize() == 2


def test_debounce_blocks_then_allows_after_threshold(tmp_path: Path) -> None:
    """The debounce helper should block immediate repeats and allow later retries."""
    queue: Queue = Queue()
    db_path = tmp_path / "ingestion_index.db"
    state_store = IngestionStateStore(db_path=db_path)
    handler = IngestionEventHandler(queue=queue, state_store=state_store)
    path = str(tmp_path / "retry.md")

    assert handler._debounce(path) is True
    assert handler._debounce(path) is False

    handler._last_seen[path] -= DEBOUNCE_SECONDS + 0.1
    assert handler._debounce(path) is True


class FakePdfPage:
    """Minimal page stub for extractor helper tests."""

    def __init__(self, text: str) -> None:
        """Create a fake PDF page.

        Parameters:
            text: Text returned by the page extraction call.
        """
        self._text = text

    def get_text(self) -> str:
        """Return the configured page text.

        Returns:
            str: Simulated extracted text.
        """
        return self._text


class FakePdfDocument:
    """Minimal PDF document stub for title detection tests."""

    def __init__(self, title: str | None) -> None:
        """Create a fake PDF document.

        Parameters:
            title: Metadata title to expose.
        """
        self.metadata = {"title": title} if title is not None else {}


def test_pdf_extractor_detects_scanned_pages() -> None:
    """Short or empty page text should be treated as scanned."""
    extractor = PDFExtractor()
    assert extractor._is_scanned(FakePdfPage("")) is True
    assert extractor._is_scanned(FakePdfPage("short text")) is True
    assert extractor._is_scanned(FakePdfPage("a" * 80)) is False


def test_pdf_extractor_detects_title_from_metadata(tmp_path: Path) -> None:
    """Metadata title should take precedence over filename."""
    extractor = PDFExtractor()
    pdf_path = tmp_path / "fallback_name.pdf"
    document = FakePdfDocument("Human Memory Systems")

    title = extractor._detect_title(pdf_path, document)

    assert title == "Human Memory Systems"


def test_pdf_extractor_falls_back_to_filename_for_missing_title(tmp_path: Path) -> None:
    """Filename stem should be used when metadata title is absent."""
    extractor = PDFExtractor()
    pdf_path = tmp_path / "fallback_name.pdf"
    document = FakePdfDocument(None)

    title = extractor._detect_title(pdf_path, document)

    assert title == "fallback_name"


def test_chunker_detects_religion_domain_and_display_header(tmp_path: Path) -> None:
    """Chunker should tag religious content and prepend a display header."""
    chunker = Chunker()
    pages = [
        ExtractedPage(
            text="## Faith\nAllah and prayer appear in this lesson about salah and tafsir.",
            page_number=1,
            source_file=str(tmp_path / "lesson.md"),
            document_title="Lesson",
            is_scanned=False,
        )
    ]

    chunks = chunker.chunk(pages, tmp_path / "lesson.md")

    assert len(chunks) >= 1
    assert chunks[0].domain == "religion"
    assert chunks[0].display_text.startswith("[Source: Lesson | Section: Faith | Page: 1]")


def test_chunker_detects_markdown_section_heading(tmp_path: Path) -> None:
    """Markdown structural headings should become section names."""
    chunker = Chunker()
    pages = [
        ExtractedPage(
            text="## Working Memory\nMemory improves with context.\n### Retrieval\nChunking matters.",
            page_number=1,
            source_file=str(tmp_path / "memory.md"),
            document_title="Memory Notes",
            is_scanned=False,
        )
    ]

    chunks = chunker.chunk(pages, tmp_path / "memory.md")

    sections = {chunk.section for chunk in chunks}
    assert "Working Memory" in sections or "Retrieval" in sections


def test_chunker_detects_content_type_transcript(tmp_path: Path) -> None:
    """Transcript-like text should be tagged as transcript content."""
    chunker = Chunker()
    pages = [
        ExtractedPage(
            text="Speaker 1: This lecture transcript explains memory systems in minute detail.",
            page_number=1,
            source_file=str(tmp_path / "talk.txt"),
            document_title="Talk",
            is_scanned=False,
        )
    ]

    chunks = chunker.chunk(pages, tmp_path / "talk.txt")

    assert chunks[0].content_type == "transcript"


class FakeEmbeddingsClient:
    """Minimal Ollama client stub for embedder tests."""

    def __init__(self) -> None:
        """Initialize the fake client state."""
        self.embedding_calls: list[str] = []

    def embeddings(self, model: str, prompt: str) -> dict:
        """Return a deterministic fake embedding vector.

        Parameters:
            model: Requested model name.
            prompt: Prompt text to embed.

        Returns:
            dict: Fake Ollama embeddings response.
        """
        self.embedding_calls.append(prompt)
        return {"embedding": [float(len(prompt)), 1.0, 2.0]}


class FakeEmbedder:
    """Minimal embedder stub exposing the `embed()` API used by VectorStore."""

    def embed(self, text: str) -> list[float]:
        """Return a deterministic embedding vector for one query string.

        Parameters:
            text: Query text to embed.

        Returns:
            list[float]: Deterministic fake vector.
        """
        return [float(len(text)), 1.0, 2.0]


class FakeBatchClient(FakeEmbeddingsClient):
    """Fake Ollama client exposing a batch embedding API."""

    def embed(self, model: str, input: list[str]) -> dict:
        """Return deterministic batch embeddings.

        Parameters:
            model: Requested model name.
            input: Batch texts.

        Returns:
            dict: Fake Ollama batch embedding response.
        """
        return {"embeddings": [[float(len(text)), 0.0] for text in input]}


def test_embedder_embed_batch_uses_batch_api_when_available() -> None:
    """Batch embedding should use the batch API when the client provides it."""
    embedder = Embedder.__new__(Embedder)
    embedder.logger = None
    embedder.client = FakeBatchClient()

    vectors = embedder._embed_batch_compat(["abc", "hello"])

    assert vectors == [[3.0, 0.0], [5.0, 0.0]]


def test_embedder_returns_empty_vector_for_blank_text() -> None:
    """Blank input should not trigger remote embedding calls."""
    embedder = Embedder.__new__(Embedder)
    embedder.logger = None
    embedder.client = FakeEmbeddingsClient()

    result = embedder.embed("   ")

    assert result == []
    assert embedder.client.embedding_calls == []


def test_embedder_falls_back_to_single_embeddings_when_batch_api_is_missing() -> None:
    """Missing batch support should fall back to per-item embedding calls."""
    embedder = Embedder.__new__(Embedder)
    embedder.logger = FakeLogger()
    embedder.client = FakeEmbeddingsClient()

    vectors = embedder._embed_batch_compat(["abc", "hello"])

    assert vectors == [[3.0, 1.0, 2.0], [5.0, 1.0, 2.0]]
    assert embedder.client.embedding_calls == ["abc", "hello"]


class FakeLogger:
    """Simple logger stub for embedder tests."""

    def info(self, *args, **kwargs) -> None:
        """Ignore info logs in tests."""

    def warning(self, *args, **kwargs) -> None:
        """Ignore warning logs in tests."""


def test_vector_store_rrf_merge_orders_highest_combined_score_first() -> None:
    """RRF merging should rank items higher when they appear in both lists."""
    store = VectorStore.__new__(VectorStore)
    merged = store._rrf_merge(
        [
            {"id": "a", "text": "A", "display_text": "A", "source_file": "a", "page_number": 1, "domain": "general"},
            {"id": "b", "text": "B", "display_text": "B", "source_file": "b", "page_number": 1, "domain": "general"},
        ],
        [
            {"id": "b", "text": "B", "display_text": "B", "source_file": "b", "page_number": 1, "domain": "general"},
            {"id": "c", "text": "C", "display_text": "C", "source_file": "c", "page_number": 1, "domain": "general"},
        ],
    )

    assert merged[0]["id"] == "b"


def test_vector_store_to_search_result_preserves_display_fields() -> None:
    """Raw LanceDB rows should convert cleanly into search results."""
    store = VectorStore.__new__(VectorStore)
    result = store._to_search_result(
        {
            "text": "content",
            "display_text": "[Source: X]\ncontent",
            "source_file": "x.md",
            "page_number": 4,
            "section": "Chapter 1",
            "domain": "education",
            "_rrf_score": 0.42,
        }
    )

    assert result.display_text.startswith("[Source: X]")
    assert result.page_number == 4
    assert result.section == "Chapter 1"
    assert result.domain == "education"
    assert result.score == 0.42


def test_vector_store_search_returns_empty_for_blank_query() -> None:
    """Blank search queries should short-circuit without hitting the table."""
    store = VectorStore.__new__(VectorStore)
    store.embedder = FakeEmbeddingsClient()
    store.table = object()

    results = store.search("   ")

    assert results == []


def test_vector_store_distance_score_is_normalized_high_is_better() -> None:
    """Distance-based rows should convert into normalized higher-is-better scores."""
    store = VectorStore.__new__(VectorStore)

    near_score = store._score_from_row({"_distance": 0.1})
    far_score = store._score_from_row({"_distance": 2.0})

    assert near_score > far_score
    assert 0 < far_score < 1


def test_pipeline_extract_pages_supports_markdown(tmp_path: Path) -> None:
    """Markdown files should be wrapped into a single extracted page."""
    file_path = tmp_path / "note.md"
    file_path.write_text("## Note\nSome content", encoding="utf-8")

    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = FakeLogger()

    pages = pipeline._extract_pages(file_path)

    assert len(pages) == 1
    assert pages[0].document_title == "note"
    assert "Some content" in pages[0].text
    assert "\t" not in pages[0].text


def test_pipeline_skips_when_no_pages_are_extracted(tmp_path: Path) -> None:
    """Files with no extractable pages should be skipped cleanly."""
    file_path = tmp_path / "empty.pdf"
    file_path.write_bytes(b"placeholder")

    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = FakeLogger()
    pipeline.state_store = FakeStateStore()
    pipeline.chunker = None
    pipeline.embedder = None
    pipeline.documents_store = None
    pipeline.personal_store = None
    pipeline._extract_pages = lambda _: []

    result = pipeline.ingest_file(file_path)

    assert result["status"] == "skipped"
    assert result["reason"] == "no_extractable_content"


def test_pipeline_appends_error_entry(tmp_path: Path, monkeypatch) -> None:
    """Pipeline error logging should append a structured entry to ERRORS.md."""
    errors_path = tmp_path / "ERRORS.md"
    errors_path.write_text("# Errors\n", encoding="utf-8")

    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = FakeLogger()

    original_open = Path.open

    def patched_open(self: Path, *args, **kwargs):
        """Redirect writes to a temporary ERRORS.md during the test.

        Parameters:
            self: Path object being opened.
            *args: Positional arguments forwarded to `Path.open`.
            **kwargs: Keyword arguments forwarded to `Path.open`.

        Returns:
            IO: Open file handle for the redirected or original path.
        """
        if self == Path("ERRORS.md"):
            return original_open(errors_path, *args, **kwargs)
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", patched_open)
    pipeline._append_error(tmp_path / "bad.pdf", RuntimeError("boom"))

    content = errors_path.read_text(encoding="utf-8")
    assert "Ingestion failure" in content
    assert "boom" in content


def test_pipeline_private_chunk_routing_helper() -> None:
    """Personal and religious chunks should be routed to the private table."""
    pipeline = IngestionPipeline.__new__(IngestionPipeline)

    personal_chunk = Chunk(
        text="text",
        display_text="display",
        source_file="a",
        page_number=1,
        section="s",
        chunk_index=0,
        domain="personal",
        content_type="note",
    )
    public_chunk = Chunk(
        text="text",
        display_text="display",
        source_file="a",
        page_number=1,
        section="s",
        chunk_index=1,
        domain="education",
        content_type="note",
    )

    assert pipeline._is_private_chunk(personal_chunk) is True
    assert pipeline._is_private_chunk(public_chunk) is False


def test_pipeline_stop_clears_threads_and_requests_watcher_stop() -> None:
    """Stopping the pipeline should signal the watcher and worker to exit."""
    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = FakeLogger()
    pipeline._stop_event = FakeStopEvent()
    pipeline.watcher = FakeWatcher()
    pipeline._worker_thread = None
    pipeline._watcher_thread = None

    pipeline.stop()

    assert pipeline._stop_event.was_set is True
    assert pipeline.watcher.stopped is True


def test_pipeline_status_reports_queue_and_store_counts() -> None:
    """Pipeline status should expose queue depth and current store counts."""
    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.queue = Queue()
    pipeline.queue.put("one")
    pipeline.watcher = FakeRunningWatcher()
    pipeline.documents_store = FakeCountStore(3)
    pipeline.personal_store = FakeCountStore(1)

    status = pipeline.status()

    assert status["queue_size"] == 1
    assert status["watcher_running"] is True
    assert status["documents_count"] == 3
    assert status["personal_count"] == 1


class FakeStateStore:
    """Simple ingestion state stub for pipeline tests."""

    def __init__(self) -> None:
        """Initialize the fake state store."""
        self.recorded_hashes: set[str] = set()

    def has_hash(self, file_hash: str) -> bool:
        """Return whether the hash has already been recorded.

        Parameters:
            file_hash: Hash value to check.

        Returns:
            bool: True when the hash was recorded earlier.
        """
        return file_hash in self.recorded_hashes

    def record_file(self, file_path: Path, file_hash: str) -> None:
        """Store a file hash in the fake state store.

        Parameters:
            file_path: Ignored file path.
            file_hash: File hash to remember.
        """
        self.recorded_hashes.add(file_hash)


class FakeStopEvent:
    """Simple stop-event stub for pipeline stop tests."""

    def __init__(self) -> None:
        """Initialize the fake stop event."""
        self.was_set = False

    def set(self) -> None:
        """Record that the stop event was triggered."""
        self.was_set = True


class FakeWatcher:
    """Simple watcher stub for pipeline stop tests."""

    def __init__(self) -> None:
        """Initialize the fake watcher."""
        self.stopped = False

    def stop(self) -> None:
        """Record that watcher stop was requested."""
        self.stopped = True


class FakeRunningWatcher:
    """Simple watcher stub exposing a running flag for status checks."""

    def __init__(self) -> None:
        """Initialize the fake watcher as running."""
        self._running = True


class FakeCountStore:
    """Simple store stub returning a fixed count."""

    def __init__(self, count_value: int) -> None:
        """Store a fixed count value.

        Parameters:
            count_value: Value returned by `count()`.
        """
        self.count_value = count_value

    def count(self) -> int:
        """Return the configured count value.

        Returns:
            int: Fixed row count.
        """
        return self.count_value


class FakeStore:
    """Simple vector store stub used for pipeline acceptance tests."""

    def __init__(self) -> None:
        """Initialize an empty in-memory add call log."""
        self.add_calls: list[tuple[list[Chunk], list[list[float]]]] = []

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Record one add call.

        Parameters:
            chunks: Chunks being stored.
            vectors: Embeddings aligned with the chunks.
        """
        self.add_calls.append((chunks, vectors))


class FakeBatchEmbedder:
    """Simple embedder stub used for pipeline acceptance tests."""

    def embed_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]:
        """Return deterministic placeholder vectors.

        Parameters:
            texts: Texts to embed.
            batch_size: Ignored batch size.

        Returns:
            list[list[float]]: Deterministic fake vectors.
        """
        return [[float(len(text)), 1.0] for text in texts]


class FakeSearchBuilder:
    """Chainable fake LanceDB search builder."""

    def __init__(self, rows: list[dict]) -> None:
        """Initialize with rows to return from `to_list()`.

        Parameters:
            rows: Search rows to return.
        """
        self.rows = rows

    def where(self, condition: str):
        """Ignore filter conditions and keep the same rows.

        Parameters:
            condition: Ignored filter expression.

        Returns:
            FakeSearchBuilder: Same builder instance.
        """
        return self

    def limit(self, count: int):
        """Limit the stored rows.

        Parameters:
            count: Maximum number of rows to retain.

        Returns:
            FakeSearchBuilder: Same builder instance with truncated rows.
        """
        self.rows = self.rows[:count]
        return self

    def to_list(self) -> list[dict]:
        """Return the prepared rows.

        Returns:
            list[dict]: Search rows.
        """
        return self.rows


class FakeHybridTable:
    """Fake table providing vector and FTS search results."""

    def __init__(self, vector_rows: list[dict], text_rows: list[dict]) -> None:
        """Initialize fake vector and keyword results.

        Parameters:
            vector_rows: Rows returned for vector search.
            text_rows: Rows returned for full-text search.
        """
        self.vector_rows = vector_rows
        self.text_rows = text_rows

    def search(self, query, query_type: str | None = None):
        """Return search rows based on the requested mode.

        Parameters:
            query: Query vector or query string.
            query_type: Optional query type, such as `fts`.

        Returns:
            FakeSearchBuilder: Builder seeded with the relevant rows.
        """
        if query_type == "fts":
            return FakeSearchBuilder([dict(row) for row in self.text_rows])
        return FakeSearchBuilder([dict(row) for row in self.vector_rows])


class FakeArabicPdfDocument:
    """Fake PDF document containing Arabic text pages."""

    def __init__(self, pages: list[FakePdfPage], title: str = "Arabic Notes") -> None:
        """Create a context-manager-compatible fake document.

        Parameters:
            pages: Page stubs to expose.
            title: Metadata title.
        """
        self._pages = pages
        self.metadata = {"title": title}

    def __enter__(self):
        """Return the fake document as a context manager."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Allow context-manager cleanup without action."""

    def __iter__(self):
        """Iterate over fake pages."""
        return iter(self._pages)


def test_watcher_detects_new_pdf(tmp_path: Path) -> None:
    """Drop a PDF, confirm it is queued for ingestion."""
    queue: Queue = Queue()
    state_store = IngestionStateStore(db_path=tmp_path / "ingestion_index.db")
    handler = IngestionEventHandler(queue=queue, state_store=state_store)
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake-but-hashable")

    handler.on_created(FakeFileEvent(pdf_path))

    assert queue.get_nowait() == pdf_path


def test_no_duplicate_ingestion(tmp_path: Path) -> None:
    """Ingest the same file twice and confirm only the first write happens."""
    file_path = tmp_path / "lesson.md"
    file_path.write_text("## Memory\nCognitive dissonance and working memory.", encoding="utf-8")

    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = FakeLogger()
    pipeline.state_store = FakeStateStore()
    pipeline.chunker = Chunker()
    pipeline.embedder = FakeBatchEmbedder()
    pipeline.documents_store = FakeStore()
    pipeline.personal_store = FakeStore()
    pipeline._extract_pages = lambda path: [
        ExtractedPage(
            text=file_path.read_text(encoding="utf-8"),
            page_number=1,
            source_file=str(file_path),
            document_title="lesson",
            is_scanned=False,
        )
    ]

    first_result = pipeline.ingest_file(file_path)
    second_result = pipeline.ingest_file(file_path)

    assert first_result["status"] == "ok"
    assert second_result["status"] == "skipped"
    assert second_result["reason"] == "already_ingested"
    assert len(pipeline.documents_store.add_calls) == 1


def test_arabic_pdf_extraction(monkeypatch, tmp_path: Path) -> None:
    """Extract text from Arabic PDF content and confirm the result is non-empty."""
    arabic_text = "هذا نص عربي طويل بما يكفي لاجتياز شرط الصفحة الممسوحة ضوئيا واختبار الاستخراج بنجاح."
    fake_document = FakeArabicPdfDocument([FakePdfPage(arabic_text)])
    monkeypatch.setattr("src.ingestion.pdf_extractor.fitz.open", lambda _: fake_document)

    extractor = PDFExtractor()
    pages = extractor.extract(tmp_path / "arabic.pdf")

    assert len(pages) == 1
    assert pages[0].text == arabic_text


def test_hybrid_search_finds_known_content() -> None:
    """Hybrid search should surface known content as the top hit."""
    store = VectorStore.__new__(VectorStore)
    store.embedder = FakeEmbedder()
    store.table = FakeHybridTable(
        vector_rows=[
            {
                "id": "1",
                "text": "Cognitive dissonance refers to mental discomfort.",
                "display_text": "[Source: psychology.pdf]\nCognitive dissonance refers to mental discomfort.",
                "source_file": "psychology.pdf",
                "page_number": 47,
                "section": "Chapter 3",
                "domain": "psychology",
                "_distance": 0.1,
            }
        ],
        text_rows=[
            {
                "id": "1",
                "text": "Cognitive dissonance refers to mental discomfort.",
                "display_text": "[Source: psychology.pdf]\nCognitive dissonance refers to mental discomfort.",
                "source_file": "psychology.pdf",
                "page_number": 47,
                "section": "Chapter 3",
                "domain": "psychology",
            }
        ],
    )

    results = store.hybrid_search("cognitive dissonance", top_k=1)

    assert len(results) == 1
    assert "Cognitive dissonance" in results[0].text


def test_domain_tagging_accuracy(tmp_path: Path) -> None:
    """Psychology-heavy text should be tagged as psychology."""
    chunker = Chunker()
    pages = [
        ExtractedPage(
            text=(
                "## Attitude Change\nFreud and cognitive therapy both discuss memory, "
                "behavioral change, attachment, and perception."
            ),
            page_number=1,
            source_file=str(tmp_path / "psychology.md"),
            document_title="Psychology",
            is_scanned=False,
        )
    ]

    chunks = chunker.chunk(pages, tmp_path / "psychology.md")

    assert chunks
    assert chunks[0].domain == "psychology"


def test_pipeline_markdown_extraction_normalizes_whitespace(tmp_path: Path) -> None:
    """Markdown extraction should normalize noisy whitespace before chunking."""
    file_path = tmp_path / "messy.md"
    file_path.write_text("## Note\r\nLine 1\t\tLine 2\r\n\r\n\r\nLine 3", encoding="utf-8")

    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = FakeLogger()

    pages = pipeline._extract_pages(file_path)

    assert len(pages) == 1
    assert "\r" not in pages[0].text
    assert "\t" not in pages[0].text
    assert "Line 1 Line 2" in pages[0].text
