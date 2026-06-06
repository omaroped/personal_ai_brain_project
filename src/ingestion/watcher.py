# MODULE: File watcher with debounce, extension filtering, and duplicate-ingest prevention.
"""Watch filesystem events and queue new files for ingestion."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from queue import Queue

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from config import WATCH_DIRS
from src.common.file_types import ALLOWED_EXTENSIONS, is_allowed_file
from src.common.logging_utils import configure_logging
from src.ingestion.state import IngestionStateStore, compute_file_hash
DEBOUNCE_SECONDS = 2.0


class IngestionEventHandler(FileSystemEventHandler):
    """Handle filesystem events and push eligible files to the ingestion queue."""

    def __init__(self, queue: Queue, state_store: IngestionStateStore) -> None:
        """Initialize the event handler.

        Parameters:
            queue: Queue receiving file paths for downstream ingestion.
            state_store: Persistent deduplication store for previously ingested files.
        """
        self.queue = queue
        self.state_store = state_store
        self.logger = configure_logging(__name__)
        self._last_seen: dict[str, float] = {}
        self._pending_paths: set[str] = set()
        self._lock = threading.Lock()

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events.

        Parameters:
            event: Watchdog event describing the filesystem change.
        """
        self._handle_event(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events.

        Parameters:
            event: Watchdog event describing the filesystem change.
        """
        self._handle_event(event)

    def _handle_event(self, event: FileSystemEvent) -> None:
        """Apply filtering, debounce, and deduplication before queueing a file.

        Parameters:
            event: Watchdog event describing the filesystem change.
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if not is_allowed_file(file_path):
            return

        path_str = str(file_path)
        if not self._debounce(path_str):
            self.logger.debug("Skipping duplicate: %s", file_path.name)
            return

        try:
            file_hash = compute_file_hash(file_path)
        except FileNotFoundError:
            self.logger.debug("Skipping transient file event: %s", file_path.name)
            return
        except PermissionError:
            self.logger.warning("Cannot access file for hashing: %s", file_path)
            return

        with self._lock:
            if self.state_store.has_hash(file_hash) or path_str in self._pending_paths:
                self.logger.debug("Skipping duplicate: %s", file_path.name)
                return

            self._pending_paths.add(path_str)

        self.queue.put(file_path)
        self.logger.info("New file queued: %s", file_path.name)

    def _debounce(self, path: str) -> bool:
        """Return whether enough time has passed to process the path again.

        Parameters:
            path: Filesystem path receiving repeated events.

        Returns:
            bool: True when the file should be processed, otherwise False.
        """
        now = time.monotonic()
        with self._lock:
            last_seen = self._last_seen.get(path)
            self._last_seen[path] = now
        return last_seen is None or (now - last_seen) > DEBOUNCE_SECONDS

    def clear_pending(self, path: Path) -> None:
        """Clear the pending marker for a file after processing completes.

        Parameters:
            path: File path that has finished processing.
        """
        with self._lock:
            self._pending_paths.discard(str(path))


class FileWatcher:
    """Watch configured directories and dispatch eligible files to an ingestion queue."""

    def __init__(self, queue: Queue, watch_dirs: list[Path] | None = None) -> None:
        """Initialize the watcher and its observer.

        Parameters:
            queue: Queue receiving file paths for downstream ingestion.
            watch_dirs: Directories to monitor. Defaults to the configured watch paths.
        """
        self.queue = queue
        self.watch_dirs = watch_dirs or WATCH_DIRS
        self.logger = configure_logging(__name__)
        self.state_store = IngestionStateStore()
        self.event_handler = IngestionEventHandler(queue=queue, state_store=self.state_store)
        self.observer = Observer()
        self._running = False

    def start(self) -> None:
        """Start the observer and block until stop is requested."""
        if self._running:
            return

        self._running = True
        for watch_dir in self.watch_dirs:
            watch_dir.mkdir(parents=True, exist_ok=True)
            self.observer.schedule(self.event_handler, str(watch_dir), recursive=True)

        self.observer.start()
        self.logger.info("File watcher started for %d directories.", len(self.watch_dirs))

        try:
            while self._running:
                time.sleep(0.2)
        finally:
            self.observer.stop()
            self.observer.join()
            self._running = False
            self.logger.info("File watcher stopped.")

    def stop(self) -> None:
        """Stop the watcher loop and underlying observer."""
        self._running = False
