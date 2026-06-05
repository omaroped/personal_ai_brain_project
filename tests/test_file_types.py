# MODULE: Focused unit tests for shared file type helpers.
"""Unit tests for allowed-extension checks and file type labels."""

from __future__ import annotations

from pathlib import Path

from src.common.file_types import get_format_label, is_supported_ingest_file


def test_is_supported_ingest_file_accepts_supported_extensions() -> None:
    """Supported ingestion extensions should return True."""
    assert is_supported_ingest_file(Path("note.md")) is True
    assert is_supported_ingest_file(Path("paper.PDF")) is True
    assert is_supported_ingest_file(Path("lesson.txt")) is True
    assert is_supported_ingest_file(Path("outline.docx")) is True


def test_is_supported_ingest_file_rejects_unknown_extensions() -> None:
    """Unknown extensions should not be accepted for ingestion."""
    assert is_supported_ingest_file(Path("image.png")) is False
    assert is_supported_ingest_file(Path("archive.zip")) is False
    assert is_supported_ingest_file(Path("no_extension")) is False


def test_get_format_label_returns_expected_labels() -> None:
    """Known extensions should map to human-readable format labels."""
    assert get_format_label(Path("paper.pdf")) == "pdf"
    assert get_format_label(Path("notes.md")) == "markdown"
    assert get_format_label(Path("notes.txt")) == "text"
    assert get_format_label(Path("notes.docx")) == "word"


def test_get_format_label_returns_unknown_for_other_extensions() -> None:
    """Unsupported extensions should map to unknown."""
    assert get_format_label(Path("image.png")) == "unknown"
