# MODULE: SQLite-backed ingestion state and file hash helpers for deduplication.
"""Ingestion state storage and file hashing helpers."""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from config import INGESTION_INDEX_DB, ensure_directories


def compute_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """Compute a SHA-256 hash for a file.

    Parameters:
        file_path: Path to the file being hashed.
        chunk_size: Number of bytes to read per iteration.

    Returns:
        str: Hex digest of the file contents.
    """
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class IngestionRecord:
    """Represents an ingested file entry stored in SQLite.

    Parameters:
        file_path: Original file path.
        file_hash: SHA-256 hash of the ingested file.
        ingested_at: ISO timestamp for ingestion time.
    """

    file_path: str
    file_hash: str
    ingested_at: str


class IngestionStateStore:
    """SQLite-backed store for tracking ingested files and preventing duplicates."""

    def __init__(self, db_path: Path = INGESTION_INDEX_DB) -> None:
        """Initialize the store and ensure the schema exists.

        Parameters:
            db_path: SQLite database path for ingestion state.
        """
        ensure_directories()
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        """Open a SQLite connection to the ingestion state database.

        Returns:
            sqlite3.Connection: Open database connection.
        """
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        """Create the ingestion index table if it does not already exist."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ingestion_index (
                    file_path TEXT NOT NULL,
                    file_hash TEXT PRIMARY KEY,
                    ingested_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def has_hash(self, file_hash: str) -> bool:
        """Check whether a file hash has already been ingested.

        Parameters:
            file_hash: SHA-256 hash to query.

        Returns:
            bool: True if the hash already exists, otherwise False.
        """
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM ingestion_index WHERE file_hash = ?",
                (file_hash,),
            ).fetchone()
        return row is not None

    def record_file(self, file_path: Path, file_hash: str) -> None:
        """Store or update an ingestion record for a file.

        Parameters:
            file_path: Path of the ingested file.
            file_hash: SHA-256 hash of the file.
        """
        ingested_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO ingestion_index (file_path, file_hash, ingested_at)
                VALUES (?, ?, ?)
                """,
                (str(file_path), file_hash, ingested_at),
            )
            connection.commit()

    def get_record(self, file_hash: str) -> IngestionRecord | None:
        """Fetch an ingestion record by hash.

        Parameters:
            file_hash: SHA-256 hash to query.

        Returns:
            IngestionRecord | None: Matching record if found, otherwise None.
        """
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT file_path, file_hash, ingested_at
                FROM ingestion_index
                WHERE file_hash = ?
                """,
                (file_hash,),
            ).fetchone()
        if row is None:
            return None
        return IngestionRecord(file_path=row[0], file_hash=row[1], ingested_at=row[2])
