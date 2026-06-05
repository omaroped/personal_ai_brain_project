# MODULE: PDF extraction with page metadata, scan detection, and optional OCR fallback.
"""Extract text and metadata from PDF files for downstream chunking."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path

import fitz

from src.common.text_normalization import full_normalization
from src.common.logging_utils import configure_logging

REFERENCE_SECTION_PATTERN = re.compile(r"^(references|bibliography|works cited)\b", re.IGNORECASE)

try:
    import pytesseract
    from PIL import Image
except ImportError:  # pragma: no cover - optional OCR stack
    pytesseract = None
    Image = None


@dataclass
class ExtractedPage:
    """Represents extracted text and metadata for one PDF page.

    Parameters:
        text: Extracted page text.
        page_number: One-based page number within the source PDF.
        source_file: Source PDF file path.
        document_title: PDF title derived from metadata or filename.
        is_scanned: Whether the page appears to require OCR.
    """

    text: str
    page_number: int
    source_file: str
    document_title: str
    is_scanned: bool


class PDFExtractor:
    """Extract clean text from PDFs with scanned-page detection and graceful fallback."""

    def __init__(self) -> None:
        """Initialize the PDF extractor."""
        self.logger = configure_logging(__name__)

    def extract(self, pdf_path: Path) -> list[ExtractedPage]:
        """Extract text from a PDF file page by page.

        Parameters:
            pdf_path: Path to the PDF file.

        Returns:
            list[ExtractedPage]: Extracted pages with metadata. Returns an empty list on failure.
        """
        pages: list[ExtractedPage] = []

        try:
            document = fitz.open(pdf_path)
        except fitz.FileDataError:
            self.logger.warning("Corrupt PDF skipped: %s", pdf_path)
            return []
        except RuntimeError as exc:
            self.logger.warning("Failed to open PDF %s: %s", pdf_path, exc)
            return []

        document_title = self._detect_title(pdf_path, document)

        with document:
            for index, page in enumerate(document, start=1):
                raw_text = page.get_text().strip()
                first_line = raw_text.splitlines()[0].strip() if raw_text.splitlines() else ""
                if REFERENCE_SECTION_PATTERN.match(first_line):
                    self.logger.info(
                        "Reference section detected in %s at page %d; remaining pages skipped.",
                        pdf_path.name,
                        index,
                    )
                    break

                is_scanned = self._is_scanned(page)
                page_text = raw_text
                if is_scanned:
                    page_text = self._extract_with_ocr(page, pdf_path, index)

                page_text = full_normalization(page_text)
                if not page_text:
                    continue

                pages.append(
                    ExtractedPage(
                        text=page_text,
                        page_number=index,
                        source_file=str(pdf_path),
                        document_title=document_title,
                        is_scanned=is_scanned,
                    )
                )

        return pages

    def _is_scanned(self, page: fitz.Page) -> bool:
        """Return whether a PDF page appears to be image-only or nearly empty.

        Parameters:
            page: PDF page object from PyMuPDF.

        Returns:
            bool: True if the page likely needs OCR.
        """
        return len(page.get_text().strip()) < 50

    def _detect_title(self, pdf_path: Path, document: fitz.Document) -> str:
        """Resolve a document title from PDF metadata or fallback filename.

        Parameters:
            pdf_path: Source PDF path.
            document: Open PyMuPDF document.

        Returns:
            str: Best-effort document title.
        """
        metadata = document.metadata or {}
        title = (metadata.get("title") or "").strip()
        return title or pdf_path.stem

    def _extract_with_ocr(self, page: fitz.Page, pdf_path: Path, page_number: int) -> str:
        """Attempt OCR extraction for a scanned page.

        Parameters:
            page: PDF page object from PyMuPDF.
            pdf_path: Source PDF path.
            page_number: One-based page number for logging.

        Returns:
            str: OCR text, or an empty string if OCR is unavailable or fails.
        """
        if pytesseract is None or Image is None:
            self.logger.warning(
                "OCR stack unavailable; scanned page skipped: %s page %d",
                pdf_path.name,
                page_number,
            )
            return ""

        try:
            pixmap = page.get_pixmap()
            image_bytes = pixmap.tobytes("png")
            image = Image.open(io.BytesIO(image_bytes))
            return pytesseract.image_to_string(image, lang="ara+eng").strip()
        except Exception as exc:  # pragma: no cover - external OCR stack variability
            self.logger.warning(
                "OCR failed for %s page %d: %s",
                pdf_path.name,
                page_number,
                exc,
            )
            return ""
