# MODULE: Unit tests for the IngestionPipeline component.
"""Test the end-to-end ingestion workflow, including directory scanning and routing."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.pipeline import IngestionPipeline


class FakeChunk:
    """Minimal chunk stub for routing tests."""

    def __init__(self, domain: str) -> None:
        """Create a minimal chunk with just the routed domain.

        Parameters:
            domain: Domain label used by `_is_private_chunk`.
        """
        self.domain = domain
        self.text = "chunk text"


@patch("src.ingestion.pipeline.is_allowed_file")
def test_pipeline_ingest_directory_scans_recursively(mock_is_allowed, tmp_path: Path) -> None:
    """Pipeline should scan all files in a directory and attempt ingestion for allowed types."""
    dir_a = tmp_path / "a"
    dir_a.mkdir()
    file1 = dir_a / "test1.md"
    file1.write_text("content 1")
    file2 = tmp_path / "test2.txt"
    file2.write_text("content 2")

    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = MagicMock()
    pipeline.ingest_file = MagicMock(return_value={"status": "ok"})

    mock_is_allowed.return_value = True

    result = pipeline.ingest_directory(tmp_path)

    assert result["processed"] == 2
    assert pipeline.ingest_file.call_count == 2


@patch("src.ingestion.pipeline.Path.open")
def test_pipeline_error_append_behavior(mock_open, tmp_path: Path) -> None:
    """Pipeline should append a structured error to ERRORS.md on failure."""
    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = MagicMock()

    mock_handle = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_handle

    pipeline._append_error(Path("bad_file.pdf"), RuntimeError("Test Error"))

    args, _ = mock_handle.write.call_args
    written_text = args[0]
    assert "ERROR AUTO-PIPELINE" in written_text
    assert "bad_file.pdf" in written_text
    assert "Test Error" in written_text


def test_pipeline_private_public_routing() -> None:
    """Chunks should be routed to personal or documents store based on domain."""
    pipeline = IngestionPipeline.__new__(IngestionPipeline)

    personal_chunk = FakeChunk("personal")
    religious_chunk = FakeChunk("religion")
    general_chunk = FakeChunk("education")

    assert pipeline._is_private_chunk(personal_chunk) is True
    assert pipeline._is_private_chunk(religious_chunk) is True
    assert pipeline._is_private_chunk(general_chunk) is False


@patch("src.ingestion.pipeline.compute_file_hash")
@patch("src.ingestion.pipeline.is_allowed_file")
def test_pipeline_skip_already_ingested(mock_is_allowed, mock_compute_hash, tmp_path: Path) -> None:
    """Pipeline should skip files that have already been recorded in the state store."""
    file_path = tmp_path / "old.md"
    file_path.write_text("old content")

    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = MagicMock()
    pipeline.state_store = MagicMock()
    pipeline.state_store.has_hash.return_value = True

    mock_is_allowed.return_value = True
    mock_compute_hash.return_value = "fixed_hash"

    result = pipeline.ingest_file(file_path)

    assert result["status"] == "skipped"
    assert result["reason"] == "already_ingested"


@patch("src.ingestion.pipeline.is_allowed_file")
def test_pipeline_skip_unsupported_file(mock_is_allowed, tmp_path: Path) -> None:
    """Pipeline should raise ValueError for unsupported file types."""
    file_path = tmp_path / "image.png"
    file_path.write_bytes(b"binary")

    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = MagicMock()

    mock_is_allowed.return_value = False

    with pytest.raises(ValueError, match="Unsupported file type"):
        pipeline.ingest_file(file_path)


@patch("src.ingestion.pipeline.is_allowed_file")
def test_pipeline_skip_no_extractable_content(mock_is_allowed, tmp_path: Path) -> None:
    """Pipeline should skip files where no pages could be extracted."""
    file_path = tmp_path / "empty.txt"
    file_path.write_text("")

    pipeline = IngestionPipeline.__new__(IngestionPipeline)
    pipeline.logger = MagicMock()
    pipeline.state_store = MagicMock()
    pipeline.state_store.has_hash.return_value = False
    pipeline._extract_pages = MagicMock(return_value=[])

    mock_is_allowed.return_value = True

    result = pipeline.ingest_file(file_path)

    assert result["status"] == "skipped"
    assert result["reason"] == "no_extractable_content"
