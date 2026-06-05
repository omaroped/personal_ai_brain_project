# MODULE: Baseline tests for shared project foundation paths, hashing, and ingestion state.
"""Baseline tests for the shared project foundation."""

from __future__ import annotations

from pathlib import Path

from config import DATA_DIR, INGESTION_INDEX_DB, LOGS_DIR, VECTORDB_DIR, ensure_directories
from src.common.health import check_path_ready
from src.ingestion.state import IngestionStateStore, compute_file_hash


def test_ensure_directories_creates_core_paths() -> None:
    """Core directories should exist after initialization."""
    ensure_directories()
    assert DATA_DIR.exists()
    assert VECTORDB_DIR.exists()
    assert LOGS_DIR.exists()


def test_compute_file_hash_is_stable(tmp_path: Path) -> None:
    """Hashing the same file twice should return the same digest."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello foundation", encoding="utf-8")

    first_hash = compute_file_hash(file_path)
    second_hash = compute_file_hash(file_path)

    assert first_hash == second_hash


def test_ingestion_state_store_records_and_reads_hash(tmp_path: Path) -> None:
    """The ingestion store should persist and retrieve file records."""
    db_path = tmp_path / "ingestion_index.db"
    store = IngestionStateStore(db_path=db_path)
    file_path = tmp_path / "document.txt"
    file_path.write_text("content", encoding="utf-8")
    file_hash = compute_file_hash(file_path)

    assert store.has_hash(file_hash) is False
    store.record_file(file_path, file_hash)
    assert store.has_hash(file_hash) is True

    record = store.get_record(file_hash)
    assert record is not None
    assert record.file_path == str(file_path)
    assert record.file_hash == file_hash


def test_check_path_ready_reports_existing_path() -> None:
    """Path health should report ready for core project directories."""
    ensure_directories()
    status = check_path_ready("ingestion_db_parent", INGESTION_INDEX_DB.parent)
    assert status.ok is True
