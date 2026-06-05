# MODULE: Shared text normalization utilities for cleaning extracted content.
"""Helpers for standardizing and cleaning raw text before chunking."""

from __future__ import annotations

import re


def cleanup_whitespace(text: str) -> str:
    """Replace multiple spaces/tabs with a single space.

    Parameters:
        text: Raw text string.

    Returns:
        str: Cleaned text string.
    """
    if not text:
        return ""
    # Replace tabs and multiple spaces with a single space
    return re.sub(r"[ \t]+", " ", text).strip()


def normalize_newlines(text: str, max_consecutive: int = 2) -> str:
    """Normalize line breaks and limit consecutive empty lines.

    Parameters:
        text: Raw text string.
        max_consecutive: Maximum number of allowed consecutive newline characters.

    Returns:
        str: Text with normalized newlines.
    """
    if not text:
        return ""
    # Standardize to \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Limit consecutive newlines
    pattern = r"\n{" + str(max_consecutive + 1) + r",}"
    replacement = "\n" * max_consecutive
    return re.sub(pattern, replacement, text).strip()


def strip_non_printable(text: str) -> str:
    """Remove non-printable characters that may pollute embeddings.

    Parameters:
        text: Raw text string.

    Returns:
        str: Text containing only printable characters and common whitespace.
    """
    if not text:
        return ""
    # Keep printable characters, newlines, and tabs
    return "".join(c for c in text if c.isprintable() or c in "\n\t")


def full_normalization(text: str) -> str:
    """Apply a full suite of normalization steps for pipeline processing.

    Parameters:
        text: Raw text string.

    Returns:
        str: Fully normalized text ready for chunking.
    """
    text = strip_non_printable(text)
    text = normalize_newlines(text)
    text = cleanup_whitespace(text)
    return text
