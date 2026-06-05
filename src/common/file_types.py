# MODULE: Shared constants and helpers for file type identification.
"""Centralized file type constants and extension filtering logic."""

from __future__ import annotations

from pathlib import Path

# Authorized extensions for ingestion
ALLOWED_EXTENSIONS: set[str] = {".pdf", ".md", ".txt", ".docx"}

def is_allowed_file(file_path: str | Path) -> bool:
    """Check if a file has an allowed extension for ingestion.

    Parameters:
        file_path: Path to the file to check.

    Returns:
        bool: True if the extension is in ALLOWED_EXTENSIONS.
    """
    path = Path(file_path)
    return path.suffix.lower() in ALLOWED_EXTENSIONS

def get_file_type_label(file_path: str | Path) -> str:
    """Return a human-readable label for the file type based on its extension.

    Parameters:
        file_path: Path to the file.

    Returns:
        str: Label such as 'pdf', 'markdown', or 'unknown'.
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    mapping = {
        ".pdf": "pdf",
        ".md": "markdown",
        ".txt": "text",
        ".docx": "word"
    }
    
    return mapping.get(ext, "unknown")
