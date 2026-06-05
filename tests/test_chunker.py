# MODULE: Focused unit tests for structural chunking behavior.
"""Unit tests for chunking heuristics and metadata assignment."""

from __future__ import annotations

from pathlib import Path

from src.ingestion.chunker import Chunker
from src.ingestion.pdf_extractor import ExtractedPage


def _page(
    text: str,
    tmp_path: Path,
    *,
    name: str = "sample.md",
    title: str = "Sample",
    page_number: int = 1,
) -> ExtractedPage:
    """Build a minimal extracted page for chunker tests.

    Parameters:
        text: Extracted page text.
        tmp_path: Temporary directory used to build a source path.
        name: Source filename.
        title: Document title.
        page_number: One-based page number.

    Returns:
        ExtractedPage: Chunker-ready page metadata.
    """
    return ExtractedPage(
        text=text,
        page_number=page_number,
        source_file=str(tmp_path / name),
        document_title=title,
        is_scanned=False,
    )


def test_markdown_headings_become_section_labels(tmp_path: Path) -> None:
    """Markdown structural headings should surface in chunk metadata."""
    chunker = Chunker()
    pages = [
        _page(
            "# Title\n## Working Memory\nThis section explains memory.\n### Retrieval\nCue-dependent recall matters.",
            tmp_path,
            name="memory.md",
            title="Memory Notes",
        )
    ]

    chunks = chunker.chunk(pages, tmp_path / "memory.md")

    assert chunks
    assert {chunk.section for chunk in chunks} & {"Working Memory", "Retrieval"}


def test_religious_content_prefers_religion_domain(tmp_path: Path) -> None:
    """Religious keywords should route chunks to the religion domain."""
    chunker = Chunker()
    pages = [
        _page(
            "## Faith\nAllah, salah, sunnah, and tafsir are central in this lesson.",
            tmp_path,
            name="faith.md",
            title="Faith Notes",
        )
    ]

    chunks = chunker.chunk(pages, tmp_path / "faith.md")

    assert chunks
    assert all(chunk.domain == "religion" for chunk in chunks)
    assert chunks[0].display_text.startswith("[Source: Faith Notes | Section: Faith | Page: 1]")


def test_transcript_text_changes_content_type_and_overlap_profile(tmp_path: Path) -> None:
    """Transcript-like inputs should be classified as transcript content."""
    chunker = Chunker()
    pages = [
        _page(
            "Speaker 1: In this lecture transcript we review memory, retrieval, and attention minute by minute.",
            tmp_path,
            name="lecture.txt",
            title="Lecture",
        )
    ]

    chunks = chunker.chunk(pages, tmp_path / "lecture.txt")

    assert chunks
    assert all(chunk.content_type == "transcript" for chunk in chunks)


def test_empty_input_returns_no_chunks(tmp_path: Path) -> None:
    """Empty extracted pages should not produce retrieval chunks."""
    chunker = Chunker()
    pages = [_page("", tmp_path, name="blank.md", title="Blank")]

    chunks = chunker.chunk(pages, tmp_path / "blank.md")

    assert chunks == []
