# MODULE: Focused unit tests for filesystem watcher event handling.
"""Unit tests for debounce, deduplication, and extension filtering in the watcher."""

from __future__ import annotations

import time
from pathlib import Path
from queue import Queue
from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.state import IngestionStateStore, compute_file_hash
from src.ingestion.watcher import DEBOUNCE_SECONDS, FileWatcher, IngestionEventHandler


class FakeFileEvent:
    """Minimal watchdog-compatible file event stub."""

    def __init__(self, path: Path, *, is_directory: bool = False) -> None:
        """Create a synthetic filesystem event.

        Parameters:
            path: Path represented by the event.
            is_directory: Whether the event points to a directory.
        """
        self.src_path = str(path)
        self.is_directory = is_directory


def _handler(tmp_path: Path) -> tuple[Queue, IngestionStateStore, IngestionEventHandler]:
    """Create an isolated event handler backed by a temporary SQLite store.

    Parameters:
        tmp_path: Temporary root path from pytest.

    Returns:
        tuple[Queue, IngestionStateStore, IngestionEventHandler]: Queue, state store, and handler.
    """
    queue: Queue = Queue()
    state_store = IngestionStateStore(db_path=tmp_path / "ingestion_index.db")
    return queue, state_store, IngestionEventHandler(queue=queue, state_store=state_store)


def test_directory_events_are_ignored(tmp_path: Path) -> None:
    """Directory events should never be queued for ingestion."""
    queue, _state_store, handler = _handler(tmp_path)
    directory = tmp_path / "notes"
    directory.mkdir()

    handler.on_created(FakeFileEvent(directory, is_directory=True))

    assert queue.empty() is True


def test_unsupported_extensions_are_filtered(tmp_path: Path) -> None:
    """Non-ingest file types should be rejected before hashing."""
    queue, _state_store, handler = _handler(tmp_path)
    file_path = tmp_path / "image.png"
    file_path.write_bytes(b"not supported")

    handler.on_created(FakeFileEvent(file_path))

    assert queue.empty() is True


def test_duplicate_hashes_in_state_store_are_skipped(tmp_path: Path) -> None:
    """Previously recorded hashes should not be queued again."""
    queue, state_store, handler = _handler(tmp_path)
    file_path = tmp_path / "paper.md"
    file_path.write_text("already ingested", encoding="utf-8")
    file_hash = compute_file_hash(file_path)
    state_store.record_file(file_path, file_hash)

    handler.on_created(FakeFileEvent(file_path))

    assert queue.empty() is True


def test_pending_paths_block_duplicate_queueing(tmp_path: Path) -> None:
    """A path already pending should not be queued a second time."""
    queue, _state_store, handler = _handler(tmp_path)
    file_path = tmp_path / "note.md"
    file_path.write_text("hello", encoding="utf-8")

    handler.on_created(FakeFileEvent(file_path))
    handler._last_seen[str(file_path)] -= DEBOUNCE_SECONDS + 0.1
    handler.on_modified(FakeFileEvent(file_path))

    assert queue.qsize() == 1


def test_clear_pending_allows_requeue_after_debounce_window(tmp_path: Path) -> None:
    """Clearing pending state should allow a later event for the same path."""
    queue, _state_store, handler = _handler(tmp_path)
    file_path = tmp_path / "note.md"
    file_path.write_text("hello", encoding="utf-8")

    handler.on_created(FakeFileEvent(file_path))
    handler.clear_pending(file_path)
    handler._last_seen[str(file_path)] -= DEBOUNCE_SECONDS + 0.1
    handler.on_modified(FakeFileEvent(file_path))

    assert queue.qsize() == 2


@patch("src.ingestion.watcher.Observer")
def test_file_watcher_starts_and_stops_observer(mock_observer_class: MagicMock, tmp_path: Path) -> None:
    """FileWatcher should correctly initialize and control the watchdog Observer."""
    mock_observer = mock_observer_class.return_value
    queue = Queue()
    watch_dir = tmp_path / "incoming"
    watch_dir.mkdir()
    
    watcher = FileWatcher(queue=queue, watch_dirs=[watch_dir])
    
    # We need to stop the loop inside start()
    def stop_immediately(*args, **kwargs):
        watcher._running = False
    
    mock_observer.start.side_effect = stop_immediately
    
    watcher.start()
    
    assert mock_observer.schedule.called
    assert mock_observer.start.called
    assert mock_observer.stop.called
    assert mock_observer.join.called


def test_debounce_logic(tmp_path: Path) -> None:
    """Verify manual debounce timing works correctly."""
    _queue, _state_store, handler = _handler(tmp_path)
    path = str(tmp_path / "debounce_test.md")

    # First event should be allowed
    assert handler._debounce(path) is True
    # Immediate second event should be blocked
    assert handler._debounce(path) is False

    # After simulated time pass, it should be allowed again
    handler._last_seen[path] -= DEBOUNCE_SECONDS + 0.1
    assert handler._debounce(path) is True
