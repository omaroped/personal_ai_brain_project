# MODULE: Structural and recursive chunking for extracted documents with domain and content tagging.
"""Chunk extracted document pages into retrieval-ready units."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHUNK_OVERLAP_DEFAULT,
    CHUNK_OVERLAP_LECTURE,
    CHUNK_OVERLAP_RELIGIOUS,
    CHUNK_SIZE_DEFAULT,
    CHUNK_SIZE_LECTURE,
    CHUNK_SIZE_RELIGIOUS,
)
from src.ingestion.auto_tagger import AutoTagger
from src.ingestion.pdf_extractor import ExtractedPage

# DOMAIN_KEYWORDS vocabulary list is moved to auto_tagger.py

MARKDOWN_HEADING_PATTERN = re.compile(r"^(#{2,3})\s+(.*)$", re.MULTILINE)


@dataclass
class Chunk:
    """Represents one chunk of retrieval-ready content.

    Parameters:
        text: Clean chunk text used for embedding.
        display_text: Chunk text with a human-readable source header.
        source_file: Source document path.
        page_number: Best-effort originating page number.
        section: Section heading or fallback label.
        chunk_index: Position of the chunk within the document.
        domain: Detected domain label.
        content_type: Detected content type label.
    """

    text: str
    display_text: str
    source_file: str
    page_number: int
    section: str
    chunk_index: int
    domain: str
    content_type: str


@dataclass
class _Section:
    """Internal structural section representation used before final chunking."""

    heading: str
    text: str
    page_number: int
    document_title: str


class Chunker:
    """Split extracted documents into structurally informed, overlap-preserving chunks."""

    def __init__(self) -> None:
        """Initialize the Chunker with a standalone AutoTagger."""
        self.tagger = AutoTagger()

    def chunk(self, pages: list[ExtractedPage], filepath: Path) -> list[Chunk]:
        """Chunk a sequence of extracted pages into retrieval-ready units.

        Parameters:
            pages: Extracted page objects from the source document.
            filepath: Original source file path.

        Returns:
            list[Chunk]: Ordered chunks derived from the input pages.
        """
        if not pages:
            return []

        content_type = self.tagger.detect_content_type("\n".join(page.text for page in pages), filepath)
        sections = self._split_structural_sections(pages, filepath)

        chunks: list[Chunk] = []
        chunk_index = 0
        for section in sections:
            domain = self.tagger.detect_domain(section.text)
            chunk_size, overlap = self._get_chunk_size(domain, content_type)
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=overlap,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            for piece in splitter.split_text(section.text):
                clean_text = piece.strip()
                if not clean_text:
                    continue
                header = (
                    f"[Source: {section.document_title} | "
                    f"Section: {section.heading} | Page: {section.page_number}]"
                )
                chunks.append(
                    Chunk(
                        text=clean_text,
                        display_text=f"{header}\n{clean_text}",
                        source_file=pages[0].source_file,
                        page_number=section.page_number,
                        section=section.heading,
                        chunk_index=chunk_index,
                        domain=domain,
                        content_type=content_type,
                    )
                )
                chunk_index += 1
        return chunks



    def _get_chunk_size(self, domain: str, content_type: str) -> tuple[int, int]:
        """Return chunk size and overlap for the document profile.

        Parameters:
            domain: Domain label.
            content_type: Content type label.

        Returns:
            tuple[int, int]: Chunk size and overlap in characters.
        """
        if domain == "religion":
            return CHUNK_SIZE_RELIGIOUS, CHUNK_OVERLAP_RELIGIOUS
        if content_type == "transcript":
            return CHUNK_SIZE_LECTURE, CHUNK_OVERLAP_LECTURE
        return CHUNK_SIZE_DEFAULT, CHUNK_OVERLAP_DEFAULT

    def _split_structural_sections(self, pages: list[ExtractedPage], filepath: Path) -> list[_Section]:
        """Split extracted pages into structural sections before recursive chunking.

        Parameters:
            pages: Extracted page objects from the source document.
            filepath: Source file path used to choose splitting logic.

        Returns:
            list[_Section]: Structural sections with headings and page hints.
        """
        if filepath.suffix.lower() == ".md":
            return self._split_markdown_sections(pages)
        return self._split_pdf_sections(pages)

    def _split_markdown_sections(self, pages: list[ExtractedPage]) -> list[_Section]:
        """Split markdown documents on `##` and `###` headings.

        Parameters:
            pages: Extracted page objects treated as markdown text.

        Returns:
            list[_Section]: Sections derived from markdown headings.
        """
        document_title = pages[0].document_title
        source_text = "\n".join(page.text for page in pages)
        matches = list(MARKDOWN_HEADING_PATTERN.finditer(source_text))
        if not matches:
            return [_Section("Unknown", source_text, pages[0].page_number, document_title)]

        sections: list[_Section] = []
        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(source_text)
            section_text = source_text[start:end].strip()
            heading = match.group(2).strip() or "Unknown"
            sections.append(
                _Section(
                    heading=heading,
                    text=section_text,
                    page_number=pages[0].page_number,
                    document_title=document_title,
                )
            )
        return sections

    def _split_pdf_sections(self, pages: list[ExtractedPage]) -> list[_Section]:
        """Split PDF content into sections based on simple heading heuristics.

        Parameters:
            pages: Extracted page objects derived from a PDF.

        Returns:
            list[_Section]: Sections inferred from heading-like lines.
        """
        sections: list[_Section] = []
        current_heading = "Unknown"
        current_page = pages[0].page_number
        current_lines: list[str] = []
        document_title = pages[0].document_title

        for page in pages:
            lines = [line.strip() for line in page.text.splitlines() if line.strip()]
            for index, line in enumerate(lines):
                if self._looks_like_pdf_heading(line, lines, index):
                    if current_lines:
                        sections.append(
                            _Section(
                                heading=current_heading,
                                text="\n".join(current_lines).strip(),
                                page_number=current_page,
                                document_title=document_title,
                            )
                        )
                        current_lines = []
                    current_heading = line
                    current_page = page.page_number
                    continue
                current_lines.append(line)

        if current_lines:
            sections.append(
                _Section(
                    heading=current_heading,
                    text="\n".join(current_lines).strip(),
                    page_number=current_page,
                    document_title=document_title,
                )
            )

        return sections or [
            _Section(
                heading="Unknown",
                text="\n".join(page.text for page in pages),
                page_number=pages[0].page_number,
                document_title=document_title,
            )
        ]

    def _looks_like_pdf_heading(self, line: str, lines: list[str], index: int) -> bool:
        """Decide whether a PDF line should be treated as a structural heading.

        Parameters:
            line: Candidate line.
            lines: All non-empty lines on the current page.
            index: Position of the candidate line.

        Returns:
            bool: True when the line looks like a heading.
        """
        if len(line) >= 80 or line.endswith("."):
            return False
        if index + 1 >= len(lines):
            return False
        next_line = lines[index + 1]
        return bool(next_line and len(next_line) > 40)
