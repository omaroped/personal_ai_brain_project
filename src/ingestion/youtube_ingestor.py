# MODULE: YouTube transcript downloader and WebVTT cleaning parser.
"""Download and clean YouTube video transcripts for vector ingestion."""

from __future__ import annotations

import logging
import re
import tempfile
from pathlib import Path

import yt_dlp

from config import DATA_DIR
from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)


class YouTubeIngestionError(Exception):
    """Raised when YouTube transcript download or parsing fails."""


def clean_vtt_content(vtt_path: Path) -> str:
    """Parse WebVTT file content, removing metadata, timestamps, tags, and duplicates.

    Parameters:
        vtt_path: Path to the WebVTT subtitle file.

    Returns:
        str: Cleaned plain-text transcript.
    """
    lines: list[str] = []
    try:
        content = vtt_path.read_text(encoding="utf-8")
    except Exception as exc:
        LOGGER.error("Failed to read subtitle file %s: %s", vtt_path, exc)
        raise YouTubeIngestionError(f"Failed to read subtitle file: {exc}") from exc

    in_style_block = False
    in_note_block = False

    for line in content.splitlines():
        line = line.strip()
        # Empty lines terminate note or style blocks
        if not line:
            in_style_block = False
            in_note_block = False
            continue

        # Detect block start and skip
        if line.upper().startswith("STYLE"):
            in_style_block = True
            continue
        if line.upper().startswith("NOTE"):
            in_note_block = True
            continue

        if in_style_block or in_note_block:
            continue

        # Skip WebVTT header metadata and timestamps
        if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line:
            continue

        # Remove formatting tags like <c.color>, <c>, <b>, etc.
        cleaned = re.sub(r"<[^>]+>", "", line).strip()
        if not cleaned:
            continue

        # Simple line deduplication for auto-generated captions which duplicate chunks
        if lines and lines[-1] == cleaned:
            continue
        lines.append(cleaned)

    return " ".join(lines)


def download_and_parse_transcript(url: str) -> dict:
    """Download the best available subtitle (Arabic or English) for a YouTube video.

    Parameters:
        url: The YouTube video URL.

    Returns:
        dict: Metadata and transcript text including title, channel, video_id, and transcript.
    """
    # Create a local temp directory inside the workspace DATA_DIR to download subtitles safely
    temp_dir_parent = DATA_DIR / "temp"
    temp_dir_parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=temp_dir_parent) as temp_dir:
        outtmpl = str(Path(temp_dir) / "sub_%(id)s")
        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["ar", "en"],
            "skip_download": True,
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except Exception as exc:
            LOGGER.error("yt-dlp extract info failed for %s: %s", url, exc)
            raise YouTubeIngestionError(f"Failed to extract info or download subtitles for {url}: {exc}") from exc

        if not info:
            raise YouTubeIngestionError(f"No info returned for URL: {url}")

        video_id = info.get("id")
        video_title = info.get("title") or f"YouTube Video {video_id}"
        channel = info.get("uploader") or "Unknown Channel"

        # Search the temporary directory for downloaded subtitle files (.vtt format)
        subtitle_files = list(Path(temp_dir).glob("*.vtt"))
        if not subtitle_files:
            raise YouTubeIngestionError(f"No Arabic or English subtitles/captions found for video: {url}")

        # Choose the best subtitle file (prefer manual, or take first)
        vtt_file = subtitle_files[0]
        cleaned_transcript = clean_vtt_content(vtt_file)

        if not cleaned_transcript.strip():
            raise YouTubeIngestionError(f"Extracted transcript text is empty for video: {url}")

        return {
            "video_id": video_id,
            "title": video_title,
            "channel": channel,
            "transcript": cleaned_transcript,
            "url": url,
        }
