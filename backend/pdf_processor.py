"""
pdf_processor.py
-----------------
Responsible for:
1. Opening a PDF file
2. Extracting text using PyMuPDF (fast, works when PDF has selectable text)
3. Falling back to Tesseract OCR ONLY when the PDF has no usable text
   (i.e. it's a scanned image-based PDF)

Keep this file simple -- no AI pipelines, just straightforward extraction.
"""

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io


def extract_text_pymupdf(pdf_path: str) -> str:
    """
    Extracts text directly from the PDF using PyMuPDF.
    Works great for PDFs that already contain selectable/typed text
    (like most GeM tender PDFs, which are HTML-to-PDF exports).
    """
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_text_ocr(pdf_path: str) -> str:
    """
    Fallback method: renders each PDF page as an image and runs
    Tesseract OCR on it. Used only when PyMuPDF finds no usable text
    (i.e. the PDF is scanned/image-based).
    """
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        text += pytesseract.image_to_string(img)
    doc.close()
    return text


def has_usable_text(text: str, min_chars: int = 30) -> bool:
    """
    Simple heuristic: if the extracted text has fewer than `min_chars`
    non-whitespace characters, we assume it's a scanned/image PDF
    and OCR is needed instead.
    """
    return len(text.strip()) >= min_chars


def process_pdf(pdf_path: str) -> dict:
    """
    Main entry point used by app.py.
    Tries PyMuPDF first; falls back to OCR only if needed.

    Returns a dict:
        {
            "text": "<full extracted text>",
            "method_used": "pymupdf" or "ocr",
            "page_count": <int>
        }
    """
    doc = fitz.open(pdf_path)
    page_count = doc.page_count
    doc.close()

    text = extract_text_pymupdf(pdf_path)

    if has_usable_text(text):
        return {
            "text": text,
            "method_used": "pymupdf",
            "page_count": page_count
        }

    # Fallback to OCR
    ocr_text = extract_text_ocr(pdf_path)
    return {
        "text": ocr_text,
        "method_used": "ocr",
        "page_count": page_count
    }


if __name__ == "__main__":
    # Quick manual test:
    # python pdf_processor.py path/to/file.pdf
    import sys
    if len(sys.argv) > 1:
        result = process_pdf(sys.argv[1])
        print("Method used:", result["method_used"])
        print("Page count:", result["page_count"])
        print("First 500 chars:\n", result["text"][:500])
    else:
        print("Usage: python pdf_processor.py <path_to_pdf>")
