# Fixture Catalog

This document lists available test fixtures and sample data for the project.

## Code-based Fixtures (tests/conftest.py)

| Name | Type | Description |
|---|---|---|
| `temp_db_path` | `pytest.fixture` | Provides a temporary path for SQLite databases. |
| `sample_pdf_content` | `pytest.fixture` | Returns a minimal PDF-like byte string for mocking. |
| `mock_extracted_page` | `pytest.fixture` | Provides a fake extracted page structure matching pymupdf output. |
| `temp_vault` | `pytest.fixture` | Creates a temporary directory structure with sample notes. |

## File-based Fixtures (tests/fixtures/)

| File | Type | Description |
|---|---|---|
| `sample_daily_review.md` | Markdown | Template for nightly review logs. |
| `sample_docx.docx` | Word | Sample DOCX file for extraction tests. |
| `sample_note.md` | Markdown | Generic markdown note. |
| `sample_personal_note.md` | Markdown | Small personal note for specific tests. |
| `sample_references_tail.txt` | Text | Text snippet for reference extraction. |
| `sample_text.txt` | Text | Simple plain text file. |
| `sample_textual.pdf` | PDF | Minimal PDF file for extraction tests. |
| `sample_transcript.txt` | Text | Mock transcript for voice/YouTube tests. |
