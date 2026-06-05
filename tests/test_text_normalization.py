# MODULE: Focused unit tests for text normalization utilities.
"""Unit tests for whitespace cleanup, newline normalization, and printable filtering."""

from __future__ import annotations

from src.common.text_normalization import (
    cleanup_whitespace,
    full_normalization,
    normalize_newlines,
    strip_non_printable,
)


def test_cleanup_whitespace_handles_tabs_and_multiple_spaces() -> None:
    """Tabs and multiple spaces should be collapsed into a single space."""
    input_text = "  Hello \t\t world   this\tis  a test  "
    # cleanup_whitespace uses strip() so leading/trailing spaces are gone
    expected = "Hello world this is a test"
    assert cleanup_whitespace(input_text) == expected


def test_cleanup_whitespace_returns_empty_for_falsy_input() -> None:
    """Empty strings or None should return empty strings."""
    assert cleanup_whitespace("") == ""
    # The function uses "if not text", so None is handled if passed despite type hints
    assert cleanup_whitespace(None) == ""  # type: ignore


def test_normalize_newlines_limits_consecutive_breaks() -> None:
    """Excessive newlines should be capped at the specified maximum."""
    input_text = "Line 1\n\n\n\nLine 2\n\n\nLine 3"
    # Default max_consecutive is 2
    expected = "Line 1\n\nLine 2\n\nLine 3"
    assert normalize_newlines(input_text) == expected


def test_normalize_newlines_standardizes_crlf() -> None:
    """Windows-style newlines should be converted to standard LF."""
    input_text = "Line 1\r\nLine 2\rLine 3"
    expected = "Line 1\nLine 2\nLine 3"
    assert normalize_newlines(input_text) == expected


def test_strip_non_printable_removes_junk_but_keeps_whitespace() -> None:
    """Control characters and non-printables should be removed."""
    # \x00 is null, \x07 is bell (non-printable)
    input_text = "Hello\x00 World\x07!\nTab\tSpace "
    expected = "Hello World!\nTab\tSpace "
    assert strip_non_printable(input_text) == expected


def test_full_normalization_applies_all_steps() -> None:
    """Full normalization should run all cleaning steps in sequence."""
    input_text = "  Hello\x00 \t\t world\n\n\n\nthis\tis \r\n a test  "
    # 1. strip_non_printable -> "  Hello \t\t world\n\n\n\nthis\tis \n a test  "
    # 2. normalize_newlines  -> "Hello \t\t world\n\nthis\tis \n a test" (strip called)
    # 3. cleanup_whitespace  -> "Hello world\n\nthis is \n a test" (tabs/spaces collapsed, strip called)
    
    normalized = full_normalization(input_text)
    assert "\x00" not in normalized
    assert "\r" not in normalized
    assert "\n\n\n" not in normalized
    assert "\t" not in normalized
    assert "  " not in normalized
    assert normalized == "Hello world\n\nthis is \n a test"
