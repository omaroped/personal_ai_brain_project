"""Tests for the ingestion state store and file hashing."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.ingestion.state import IngestionStateStore, compute_file_hash


def test_compute_file_hash_stability(tmp_path: Path) -> None:
    """Hashing the same content should always return the same hash."""
    file = tmp_path / "test.txt"
    file.write_text("consistent content", encoding="utf-8")
    
    hash1 = compute_file_hash(file)
    hash2 = compute_file_hash(file)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 length


def test_state_store_lifecycle(temp_db_path: Path, tmp_path: Path) -> None:
    """Store should record, check, and retrieve file state."""
    store = IngestionStateStore(db_path=temp_db_path)
    
    test_file = tmp_path / "ingest.md"
    test_file.write_text("hello", encoding="utf-8")
    test_hash = compute_file_hash(test_file)
    
    # Initial state
    assert store.has_hash(test_hash) is False
    
    # Record
    store.record_file(test_file, test_hash)
    assert store.has_hash(test_hash) is True
    
    # Retrieve
    record = store.get_record(test_hash)
    assert record is not None
    assert record.file_hash == test_hash
    assert record.file_path == str(test_file)


def test_state_store_no_duplicate_error(temp_db_path: Path, tmp_path: Path) -> None:
    """Recording the same hash twice should not raise an error (handled by REPLACE)."""
    store = IngestionStateStore(db_path=temp_db_path)
    test_file = tmp_path / "dup.txt"
    test_file.write_text("data", encoding="utf-8")
    test_hash = compute_file_hash(test_file)
    
    store.record_file(test_file, test_hash)
    # Should not raise
    store.record_file(test_file, test_hash)
