"""
HireShield Multi-Input Scanner API Endpoints.

Provides endpoints for:
- PDF document scanning: POST /api/scanner/analyze-pdf and POST /api/scan/pdf
- Google Forms / recruitment forms scanning: POST /api/scanner/analyze-form and POST /api/scan/form
- Pasted job text scanning: POST /api/scanner/analyze-text and POST /api/scan/text
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from pydantic import BaseModel, Field

from app.models.user import User
from app.services.auth_service import get_optional_current_user
from app.services.pdf_service import extract_text_from_pdf, MAX_PDF_SIZE_BYTES
from app.services.form_service import extract_form_content
from app.services.risk_pipeline import run_central_risk_pipeline
from app.services.pdf_service import extract_links_from_text

logger = logging.getLogger("hireshield.api.scanner")

router = APIRouter(tags=["Multi-Input Scanner"])


class FormScanRequest(BaseModel):
    url: str = Field(..., description="Google Form or recruitment form URL")


class TextScanRequest(BaseModel):
    text: Optional[str] = Field(None, description="Pasted job description or recruitment message text")
    content: Optional[str] = Field(None, description="Alias for text")
    title: Optional[str] = Field(None, description="Optional job title")
    company: Optional[str] = Field(None, description="Optional claimed employer name")


@router.post("/scanner/analyze-pdf")
@router.post("/scan/pdf")
async def analyze_pdf_endpoint(
    file: UploadFile = File(...),
    company: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Receives an uploaded PDF (job offer letter, appointment letter, contract),
    extracts readable text, normalizes it, and processes it through the central risk engine.
    Gracefully handles scanned/image-based PDFs with actionable guidance.
    """
    filename = file.filename or "uploaded_document.pdf"
    content_type = file.content_type or ""

    logger.info(f"PDF scan requested for: {filename} (Content-Type: {content_type})")

    # Validate file extension or MIME type
    if not filename.lower().endswith(".pdf") and "pdf" not in content_type.lower():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid file format. Please upload a valid PDF document (.pdf)."
        )

    # Read bytes safely
    try:
        pdf_bytes = await file.read()
    except Exception as read_err:
        logger.error(f"Error reading uploaded PDF {filename}: {read_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {str(read_err)}"
        )

    if len(pdf_bytes) > MAX_PDF_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Uploaded PDF exceeds the maximum file size limit of 10 MB ({len(pdf_bytes) / (1024 * 1024):.1f} MB uploaded)."
        )

    # Extract text using service
    extract_res = extract_text_from_pdf(pdf_bytes, filename=filename)

    if not extract_res["success"]:
        # Scanned document or empty text
        if extract_res.get("is_scanned_image"):
            return {
                "success": False,
                "status": "NO_EXTRACTABLE_TEXT",
                "score": None,
                "risk_score": None,
                "risk_level": "INCOMPLETE",
                "verdict": "INCOMPLETE",
                "input_type": "PDF",
                "inputType": "PDF",
                "message": extract_res["message"],
                "summary": extract_res["message"],
                "explanation": extract_res["message"],
                "fallback_available": True,
                "is_scanned_image": True,
                "filename": filename,
                "page_count": extract_res.get("page_count", 0),
                "signals": [],
                "red_flags": [],
                "categories": {},
                "recommendations": [
                    "Use the Paste Job Text scanner tab to copy and paste the readable text.",
                    "If this is a physical paper document, type the key terms, salary claims, and requested fees into HireShield.",
                    "Do not pay any upfront fees or transfer money requested in unverified documents."
                ],
            }

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=extract_res["message"]
        )

    extracted_text = extract_res["text"]
    extracted_urls = extract_res.get("extracted_urls", [])

    doc_title = title or f"Document: {filename}"
    doc_company = company or None
    user_id = current_user.id if current_user else None

    # Run through the single central risk pipeline
    result = run_central_risk_pipeline(
        input_type="PDF",
        text=extracted_text,
        url=extracted_urls[0] if extracted_urls else None,
        title=doc_title,
        company=doc_company,
        external_urls=extracted_urls,
        metadata={"filename": filename, "page_count": extract_res.get("page_count", 1)},
        user_id=user_id,
        auto_persist=True
    )

    result["filename"] = filename
    result["page_count"] = extract_res.get("page_count", 1)
    result["extracted_urls"] = extracted_urls

    return result


@router.post("/scanner/analyze-form")
@router.post("/scan/form")
def analyze_form_endpoint(
    payload: FormScanRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Receives a Google Form or recruitment form URL, retrieves publicly accessible
    form elements (title, description, fields, questions), and passes them through
    the central risk engine.
    """
    raw_url = payload.url.strip() if payload.url else ""
    if not raw_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A recruitment form URL must be provided."
        )

    logger.info(f"Form scan requested for URL: {raw_url}")

    # Fetch form content
    form_res = extract_form_content(raw_url)

    if not form_res["success"]:
        # Do not invent fake results if restricted/private
        return {
            "success": False,
            "status": form_res.get("status", "FORM_ACCESS_RESTRICTED"),
            "score": None,
            "risk_score": None,
            "risk_level": "INCOMPLETE",
            "verdict": "INCOMPLETE",
            "input_type": "GOOGLE_FORM",
            "inputType": "GOOGLE_FORM",
            "url": raw_url,
            "message": form_res.get("message", "Unable to access the form automatically."),
            "summary": form_res.get("message", "Unable to access the form automatically."),
            "explanation": form_res.get("message", "Unable to access the form automatically."),
            "fallback_available": True,
            "job": {
                "title": form_res.get("title") or "Restricted Recruitment Form",
                "text_preview": form_res.get("message", "Access restricted."),
            },
            "signals": [],
            "red_flags": [],
            "categories": {},
            "recommendations": [
                "Copy the form questions and paste them directly into HireShield's Paste Job Text tab.",
                "Verify whether the organization uses official Google Workspace forms or corporate career portals.",
                "Legitimate employers never ask for Aadhaar, PAN, bank passwords, or upfront fees via unverified forms."
            ],
        }

    combined_text = form_res.get("combined_text", "")
    external_urls = form_res.get("external_urls", [])
    title = form_res.get("title", "Google Form Recruitment Application")
    user_id = current_user.id if current_user else None

    # Run through the single central risk pipeline
    result = run_central_risk_pipeline(
        input_type="GOOGLE_FORM",
        text=combined_text,
        url=form_res.get("final_url") or raw_url,
        title=title,
        external_urls=external_urls,
        metadata={"fields_count": len(form_res.get("fields", []))},
        user_id=user_id,
        auto_persist=True
    )

    result["fields"] = form_res.get("fields", [])
    result["external_urls"] = external_urls

    return result


@router.post("/scanner/analyze-text")
@router.post("/scan/text")
def analyze_text_endpoint(
    payload: TextScanRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """
    Receives raw job description or recruitment message text (e.g. copied from WhatsApp,
    Telegram, email, or job portal) and passes it through the central risk engine.
    """
    raw_text = (payload.text or payload.content or "").strip()
    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Job text cannot be empty. Please paste the job description or recruitment message."
        )

    if len(raw_text) < 15:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The provided job text is too brief to evaluate (minimum 15 characters required)."
        )

    if len(raw_text) > 50000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The provided job text exceeds the maximum permissible limit of 50,000 characters."
        )

    title = (payload.title or "").strip() or "Pasted Job Description"
    company = (payload.company or "").strip() or None

    # Harvest any embedded URLs
    embedded_urls = extract_links_from_text(raw_text)
    user_id = current_user.id if current_user else None

    # Run through the single central risk pipeline
    result = run_central_risk_pipeline(
        input_type="TEXT",
        text=raw_text,
        url=embedded_urls[0] if embedded_urls else None,
        title=title,
        company=company,
        external_urls=embedded_urls,
        user_id=user_id,
        auto_persist=True
    )

    result["embedded_urls"] = embedded_urls
    return result
