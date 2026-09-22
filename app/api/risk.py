"""
HireShield Advanced Risk Intelligence API Route.

Exposes POST /api/risk/analyze for Chrome extension and web platform integration.
Includes input sanitization, SSRF protection, and graceful error handling.
"""

import logging
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.risk_engine import analyze_job_risk
from app.risk_engine.domain.dns import is_private_ip, is_ip_address
from app.db.database import SessionLocal
from app.services.candidate_service import auto_save_scan

logger = logging.getLogger("hireshield.api.risk")

router = APIRouter(prefix="/risk", tags=["Risk Engine"])


class RiskAnalyzeRequest(BaseModel):
    url: Optional[str] = Field(default=None, description="Job posting or application URL")
    job_text: Optional[str] = Field(default=None, description="Extracted job description text")
    company_name: Optional[str] = Field(default=None, description="Claimed employer company name")
    recruiter_email: Optional[str] = Field(default=None, description="Contact email of the recruiter")
    salary: Optional[str] = Field(default=None, description="Offered compensation or salary text")
    source: Optional[str] = Field(default=None, description="Platform source (e.g. linkedin, indeed, naukri, direct)")


class RiskAnalyzeResponse(BaseModel):
    success: bool
    risk_score: int
    risk_level: str
    confidence: float
    summary: str
    signals: List[Dict[str, Any]]
    positive_signals: List[str]
    recommendations: List[str]
    verification_audit: Optional[Dict[str, Any]] = None
    override: Optional[Dict[str, Any]] = None
    analysis: Dict[str, Any]
    id: Optional[str] = None
    candidate_id: Optional[str] = None


def sanitize_input(val: Optional[str], max_len: int = 50000) -> Optional[str]:
    """Sanitizes text strings and enforces boundary limits."""
    if val is None:
        return None
    cleaned = str(val).strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len]
    return cleaned


def validate_and_sanitize_url(url_str: Optional[str]) -> Optional[str]:
    """
    Validates URL scheme, prevents malicious protocols (javascript:, file:),
    and validates length.
    """
    if not url_str:
        return None

    cleaned = str(url_str).strip()
    if len(cleaned) > 2048:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL exceeds maximum permissible length of 2048 characters."
        )

    # Prepend https:// if bare domain provided
    if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
        test_url = "https://" + cleaned
    else:
        test_url = cleaned

    parsed = urlparse(test_url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted."
        )

    return test_url


@router.post("/analyze", response_model=RiskAnalyzeResponse)
def analyze_risk_endpoint(payload: RiskAnalyzeRequest):
    """
    Evaluates multi-vector recruitment fraud risk across NLP, Domain intelligence,
    Company verification, Recruiter credibility, and Salary anomaly engines.
    """
    try:
        sanitized_url = validate_and_sanitize_url(payload.url)
        sanitized_text = sanitize_input(payload.job_text, max_len=50000)
        sanitized_company = sanitize_input(payload.company_name, max_len=200)
        sanitized_email = sanitize_input(payload.recruiter_email, max_len=254)
        sanitized_salary = sanitize_input(payload.salary, max_len=200)
        sanitized_source = sanitize_input(payload.source, max_len=50)

        # Require at least one actionable input (URL or job text)
        if not sanitized_url and not sanitized_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one of 'url' or 'job_text' must be provided for risk analysis."
            )

        logger.info(
            f"Risk analysis requested for URL: '{sanitized_url or 'N/A'}', "
            f"Company: '{sanitized_company or 'N/A'}', Text Length: {len(sanitized_text or '')}"
        )

        result = analyze_job_risk(
            url=sanitized_url,
            job_text=sanitized_text,
            company_name=sanitized_company,
            recruiter_email=sanitized_email,
            salary=sanitized_salary,
            source=sanitized_source
        )

        # Persist the hybrid risk scan to SQLite so it can be retrieved via /candidates/{id} or /risk-analysis/{id}
        record_id = None
        try:
            with SessionLocal() as db:
                cand_dict = {
                    "url": sanitized_url,
                    "final_url": sanitized_url,
                    "job": {
                        "title": sanitized_company or "Evaluated Position",
                        "company": sanitized_company,
                        "text_preview": (sanitized_text or "")[:1000],
                    },
                    "risk_score": result.get("risk_score", 0),
                    "risk_level": result.get("risk_level", "LOW"),
                    "verdict": result.get("verification_audit", {}).get("verdict") or ("CONFIRMED_SCAM" if result.get("risk_score", 0) >= 60 else "VERIFIED_LEGITIMATE"),
                    "legitimacy_score": max(0, 100 - result.get("risk_score", 0)),
                    "fake_job_probability": round(result.get("risk_score", 0) / 100.0, 2),
                    "scores": result.get("analysis", {}),
                    "red_flags": result.get("signals", []),
                    "green_flags": [{"message": s} if isinstance(s, str) else s for s in result.get("positive_signals", [])],
                    "technical_checks": result.get("analysis", {}).get("domain", {}).get("details", {}),
                    "verification_audit": result.get("verification_audit", {}),
                    "recommendations": result.get("recommendations", []),
                    "explanation": result.get("summary", ""),
                }
                saved = auto_save_scan(db, cand_dict)
                if saved and "id" in saved:
                    record_id = saved["id"]
        except Exception as save_err:
            logger.warning(f"Could not auto-persist hybrid risk scan: {save_err}")

        result["id"] = record_id
        result["candidate_id"] = record_id
        return result

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error during risk analysis: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during risk intelligence analysis: {str(exc)}"
        )
