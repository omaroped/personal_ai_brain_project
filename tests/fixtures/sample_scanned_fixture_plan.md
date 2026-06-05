# Plan: Scanned PDF Fixture Generation

## Objective
Create a PDF that contains no extractable text, forcing the ingestion pipeline to trigger the OCR (Optical Character Recognition) fallback path.

## Generation Steps
1. **Create Source Image:**
   - Create a simple image (PNG or JPG) with text like: "This is a scanned document for OCR testing."
   - Use a clear sans-serif font (Arial/Helvetica) at 12pt.
2. **Convert to PDF:**
   - Convert the image to a PDF file where the page is a single large image object with no text layer.
   - Using `img2pdf`: `img2pdf source.png -o sample_scanned.pdf`
   - Using `pymupdf` (Python):
     ```python
     import fitz
     doc = fitz.open()
     img = open("source.png", "rb").read()
     page = doc.new_page()
     page.insert_image(page.rect, stream=img)
     doc.save("sample_scanned.pdf")
     ```

## Expected OCR Behavior
- **Detection:** `PDFExtractor._is_scanned()` should return `True` because `page.get_text()` returns an empty string or very short noise.
- **Extraction:** `pytesseract` should be invoked to process the image.
- **Output:** The extracted text should contain the source image string with > 90% character accuracy.

## Repository Placeholder
A real binary `sample_scanned.pdf` should be placed in `tests/fixtures/` following these steps.
