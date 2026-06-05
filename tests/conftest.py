"""Shared fixtures and configuration for the test suite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Provide a path to a temporary SQLite database."""
    return tmp_path / "test_ingestion.db"


@pytest.fixture
def sample_pdf_content() -> bytes:
    """Return a minimal valid PDF-like byte string for mocking."""
    # A real minimal PDF is complex, so we'll use a placeholder for now
    # until a real fixture file is added.
    return b"%PDF-1.4\n1 0 obj\n<< /Title (Test Doc) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"


@pytest.fixture
def mock_extracted_page() -> dict:
    """Provide a fake extracted page structure matching pymupdf extractor output."""
    return {
        "text": "This is a sample extracted text from a PDF page.",
        "page_number": 1,
        "metadata": {
            "title": "Sample Document",
            "author": "Test Author",
            "creation_date": "2026-06-06"
        }
    }


@pytest.fixture
def temp_vault(tmp_path: Path) -> Path:
    """Create a temporary vault structure for testing."""
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "note1.md").write_text("Note 1 content", encoding="utf-8")
    (vault / "note2.txt").write_text("Note 2 content", encoding="utf-8")
    return vault
