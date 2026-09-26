"""
HireShield PDF Ingestion and Text Extraction Service.

Extracts text from job offer letters, employment contracts, and recruitment documents
with scanned document detection, link harvesting, and an extensible OCR fallback hook.
"""

import io
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pypdf import PdfReader

logger = logging.getLogger("hireshield.services.pdf")

MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_EXTRACTED_CHARS = 60000


def ocr_fallback_hook(pdf_bytes: bytes) -> Optional[str]:
    """
    Extensible plug-in hook for Optical Character Recognition (OCR).
    
    If OCR libraries (e.g., pytesseract, EasyOCR, or cloud vision API) are integrated
    in the future, this hook can be implemented without redesigning the scanner.
    Currently returns None to signal that pure digital text extraction was performed.
    """
    # Placeholder for optional OCR integration
    return None


def extract_links_from_text(text: str) -> List[str]:
    """Extracts HTTP/HTTPS URLs present within document text."""
    url_pattern = re.compile(r"https?://[^\s<>\"'{}|\\^`\[\]]+", re.I)
    matches = url_pattern.findall(text)
    # Deduplicate while preserving order
    return list(dict.fromkeys(matches))[:10]


def normalize_pdf_text(raw_text: str) -> str:
    """Normalizes extracted PDF text by removing control characters and collapsing whitespace."""
    if not raw_text:
        return ""
    # Strip null bytes and non-printable control chars except tabs/newlines
    cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", " ", raw_text)
    # Normalize multiple whitespace characters
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    # Normalize excessive newlines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_text_from_pdf(
    pdf_bytes: bytes,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parses a PDF file from bytes, extracts all digital page text,
    discovers embedded URLs, and detects scanned/image-only documents.
    """
    filename = filename or "document.pdf"

    # 1. Basic validation
    if not pdf_bytes or len(pdf_bytes) == 0:
        return {
            "success": False,
            "error_type": "EMPTY_FILE",
            "message": "The uploaded PDF file is empty (0 bytes). Please upload a valid recruitment PDF.",
            "is_scanned_image": False,
            "text": "",
            "page_count": 0,
            "extracted_urls": [],
            "filename": filename,
        }

    if len(pdf_bytes) > MAX_PDF_SIZE_BYTES:
        return {
            "success": False,
            "error_type": "FILE_TOO_LARGE",
            "message": f"PDF file size ({len(pdf_bytes) / (1024 * 1024):.1f} MB) exceeds the maximum limit of 10 MB.",
            "is_scanned_image": False,
            "text": "",
            "page_count": 0,
            "extracted_urls": [],
            "filename": filename,
        }

    # 2. Check magic header (%PDF-)
    if not pdf_bytes.startswith(b"%PDF-"):
        # Some PDFs may have a few leading bytes/whitespace before %PDF-
        if b"%PDF-" not in pdf_bytes[:1024]:
            return {
                "success": False,
                "error_type": "INVALID_PDF_FORMAT",
                "message": "The uploaded file does not appear to be a valid PDF document.",
                "is_scanned_image": False,
                "text": "",
                "page_count": 0,
                "extracted_urls": [],
                "filename": filename,
            }

    # 3. Read PDF stream with pypdf
    try:
        stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(stream)
        num_pages = len(reader.pages)
    except Exception as exc:
        logger.warning(f"Error parsing PDF structure ({filename}): {exc}")
        return {
            "success": False,
            "error_type": "CORRUPTED_PDF",
            "message": f"Unable to parse the PDF document. The file may be password-protected or corrupted: {str(exc)}",
            "is_scanned_image": False,
            "text": "",
            "page_count": 0,
            "extracted_urls": [],
            "filename": filename,
        }

    # 4. Extract text from pages
    page_texts: List[str] = []
    annotation_urls: List[str] = []

    for page_idx, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
            if txt.strip():
                page_texts.append(txt.strip())

            # Extract any embedded hyperlink annotations
            if "/Annots" in page:
                try:
                    annots = page["/Annots"]
                    if annots:
                        for annot in annots:
                            annot_obj = annot.get_object() if hasattr(annot, "get_object") else annot
                            if isinstance(annot_obj, dict) and "/A" in annot_obj:
                                action = annot_obj["/A"]
                                if isinstance(action, dict) and "/URI" in action:
                                    uri = str(action["/URI"])
                                    if uri.startswith("http://") or uri.startswith("https://"):
                                        annotation_urls.append(uri)
                except Exception as annot_err:
                    logger.debug(f"Annotation parse error on page {page_idx}: {annot_err}")
        except Exception as page_err:
            logger.warning(f"Error extracting text from page {page_idx} of {filename}: {page_err}")

    raw_combined_text = "\n\n".join(page_texts)
    normalized_text = normalize_pdf_text(raw_combined_text)

    # 5. Check if document has no extractable digital text (scanned image or empty)
    if len(normalized_text) < 30:
        # Try extensible OCR fallback hook
        ocr_text = ocr_fallback_hook(pdf_bytes)
        if ocr_text and len(ocr_text.strip()) >= 30:
            normalized_text = normalize_pdf_text(ocr_text)
        else:
            return {
                "success": False,
                "error_type": "NO_EXTRACTABLE_TEXT",
                "message": (
                    "The uploaded PDF contains no extractable digital text (it may be a scanned document or image). "
                    "OCR processing is required for scanned documents, or you can paste the text manually into the Paste Job Text scanner."
                ),
                "is_scanned_image": True,
                "text": "",
                "page_count": num_pages,
                "extracted_urls": [],
                "filename": filename,
                "fallback_available": True,
            }

    # Cap text length
    if len(normalized_text) > MAX_EXTRACTED_CHARS:
        normalized_text = normalized_text[:MAX_EXTRACTED_CHARS]

    # Combine text links + annotation links
    all_links = extract_links_from_text(normalized_text)
    for u in annotation_urls:
        if u not in all_links:
            all_links.append(u)

    logger.info(f"Extracted {len(normalized_text)} chars across {num_pages} pages from '{filename}', found {len(all_links)} links.")

    return {
        "success": True,
        "error_type": None,
        "message": f"Successfully extracted text from {num_pages} page(s).",
        "is_scanned_image": False,
        "text": normalized_text,
        "page_count": num_pages,
        "extracted_urls": all_links,
        "filename": filename,
        "fallback_available": False,
    }
