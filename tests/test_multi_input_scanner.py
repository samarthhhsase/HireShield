"""
Automated Test Suite for HireShield Multi-Input Recruitment Scam Scanner.

Tests:
1. Pasted Text Scanner: Legitimate jobs, registration fees, government ID harvesting, salary/urgency anomalies.
2. PDF Scanner: Legitimate PDF, scam offer PDF, empty/scanned PDF, invalid PDF.
3. Google Form Scanner: Legitimate form, sensitive info harvesting form, payment instruction form, restricted/private form.
4. Regression Tests: Existing URL scanner, browser fallback, and Chrome extension endpoints.
"""

import io
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.main import app

client = TestClient(app)


def create_in_memory_pdf(text_content: str) -> bytes:
    """Helper to generate a valid PDF byte string with extractable digital text."""
    writer = PdfWriter()
    # Create a page with simple content
    # Note: pypdf can create blank pages, or we can use standard minimal PDF structure with a text stream
    # A standard valid minimal text PDF:
    stream_content = f"BT /F1 12 Tf 72 712 Td ({text_content[:2000]}) Tj ET".encode("latin-1", errors="replace")
    writer.add_blank_page(width=612, height=792)
    
    # Write to buffer
    buf = io.BytesIO()
    writer.write(buf)
    base_pdf = buf.getvalue()

    # If text is needed in the PDF, pypdf writes pages; let's use reportlab if available or build valid PDF with text stream
    # Let's check: can we insert a text object into pypdf page?
    # Simple, foolproof way to create a valid searchable PDF in pure python:
    pdf_template = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        b"4 0 obj << /Length " + str(len(text_content) + 50).encode("ascii") + b" >>\n"
        b"stream\n"
        b"BT\n"
        b"/F1 12 Tf\n"
        b"72 712 Td\n"
        b"(" + text_content.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1", errors="replace") + b") Tj\n"
        b"ET\n"
        b"endstream\n"
        b"endobj\n"
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        b"xref\n"
        b"0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000244 00000 n \n"
        b"0000000350 00000 n \n"
        b"trailer << /Size 6 /Root 1 0 R >>\n"
        b"startxref\n"
        b"430\n"
        b"%%EOF\n"
    )
    return pdf_template


# ============================================================================
# 1. TEXT SCANNER TESTS
# ============================================================================

def test_text_scanner_legitimate_job():
    """Verify that a legitimate corporate job description gets a low risk score."""
    legit_text = (
        "Senior Cloud Architect needed at Acme Technology Corp. "
        "Minimum 5 years experience with distributed systems, Kubernetes, and Go. "
        "Standard multi-round technical interview and system design evaluation. "
        "We offer comprehensive medical insurance, 401(k) matching, and paid time off. "
        "Equal Opportunity Employer. We never charge any application or recruitment fees."
    )
    resp = client.post("/api/scanner/analyze-text", json={"text": legit_text, "title": "Senior Cloud Architect"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["input_type"] == "TEXT"
    assert data["risk_score"] < 35
    assert data["risk_level"] == "LOW"
    assert data["verdict"] == "VERIFIED_LEGITIMATE"
    assert "categories" in data
    assert data["categories"]["financial_risk"]["level"] == "Low"
    assert len(data["recommendations"]) > 0


def test_text_scanner_fake_job_registration_fee():
    """Verify that a job demanding upfront registration/training fees triggers CRITICAL risk."""
    scam_text = (
        "URGENT HIRING! Work From Home Data Entry Operator. Earn ₹50,000 per month! "
        "Guaranteed selection without any interview. "
        "All candidates must pay a mandatory registration fee of ₹2,999 immediately via UPI to confirm your position. "
        "Contact recruiter only on WhatsApp at +91 9876543210."
    )
    resp = client.post("/api/scanner/analyze-text", json={"text": scam_text, "title": "Data Entry Job"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["risk_score"] >= 75
    assert data["risk_level"] == "CRITICAL"
    assert data["verdict"] == "CONFIRMED_SCAM"
    assert data["categories"]["financial_risk"]["level"] in ("High", "Critical")
    # Verify fee warning sign is present
    signals_text = " ".join(s.get("title", "").lower() + " " + s.get("description", "").lower() for s in data["signals"])
    assert "fee" in signals_text or "payment" in signals_text


def test_text_scanner_aadhaar_pan_harvesting():
    """Verify that demanding government ID / banking upfront triggers CRITICAL risk override."""
    harvest_text = (
        "Immediate Opening for Customer Service Executive. "
        "To register and confirm your interview, you must upload your Aadhaar Card, PAN Card, and bank account details. "
        "Share your OTP verification code received on mobile to activate your candidate profile."
    )
    resp = client.post("/api/scanner/analyze-text", json={"text": harvest_text})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["risk_score"] >= 75
    assert data["risk_level"] == "CRITICAL"
    assert data["categories"]["identity_risk"]["level"] in ("High", "Critical")
    # Check recommendations mention identity safety
    recs_text = " ".join(data["recommendations"]).lower()
    assert "aadhaar" in recs_text or "identity" in recs_text or "bank" in recs_text


def test_text_scanner_unrealistic_salary_and_urgency():
    """Verify that unrealistic salary claims and artificial urgency increase risk."""
    urgency_text = (
        "HURRY! ONLY 2 SEATS LEFT! APPLY IMMEDIATELY OR LOSE YOUR CHANCE! "
        "Earn $500 daily with just 1 hour of simple copy paste work on your smartphone! "
        "No skills, no qualification needed. 100% guaranteed income!"
    )
    resp = client.post("/api/scanner/analyze-text", json={"text": urgency_text})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["risk_score"] >= 25
    assert data["risk_level"] in ("MEDIUM", "MODERATE", "HIGH", "CRITICAL")
    assert data["categories"]["behavioral_risk"]["score"] > 0


def test_text_scanner_empty_and_short_input_validation():
    """Verify validation for empty and too-short text inputs."""
    resp_empty = client.post("/api/scanner/analyze-text", json={"text": ""})
    assert resp_empty.status_code == 422

    resp_short = client.post("/api/scanner/analyze-text", json={"text": "Quick hiring"})
    assert resp_short.status_code == 422


# ============================================================================
# 2. PDF SCANNER TESTS
# ============================================================================

def test_pdf_scanner_legitimate_offer():
    """Verify scanning a legitimate employment letter in PDF format."""
    legit_doc = (
        "APPOINTMENT LETTER - ACME CORP. "
        "We are pleased to offer you the position of Systems Engineer. "
        "Your compensation package includes standard base salary and health insurance benefits. "
        "Formal onboarding will take place at our corporate headquarters. "
        "Equal opportunity employer. Please sign and return this document."
    )
    pdf_bytes = create_in_memory_pdf(legit_doc)
    files = {"file": ("offer_letter.pdf", pdf_bytes, "application/pdf")}
    resp = client.post("/api/scanner/analyze-pdf", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["input_type"] == "PDF"
    assert data["risk_score"] < 40
    assert data["filename"] == "offer_letter.pdf"
    assert "categories" in data
    assert data["categories"]["technical_risk"]["status"] == "UNAVAILABLE"  # No URL in PDF


def test_pdf_scanner_scam_job_offer():
    """Verify scanning a fraudulent appointment letter PDF demanding fees and Aadhaar."""
    scam_doc = (
        "PROVISIONAL APPOINTMENT LETTER - IMMEDIATE JOINING. "
        "Congratulations! You are selected as Senior Manager with ₹1,20,000 monthly salary. "
        "No interview required. To confirm your position, pay ₹4,500 refundable security deposit. "
        "Send your Aadhaar Card copy and UPI transaction reference number immediately."
    )
    pdf_bytes = create_in_memory_pdf(scam_doc)
    files = {"file": ("scam_appointment.pdf", pdf_bytes, "application/pdf")}
    resp = client.post("/api/scanner/analyze-pdf", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["input_type"] == "PDF"
    assert data["risk_score"] >= 75
    assert data["risk_level"] == "CRITICAL"
    assert data["categories"]["financial_risk"]["level"] in ("High", "Critical")
    assert data["categories"]["identity_risk"]["level"] in ("High", "Critical")


def test_pdf_scanner_empty_or_scanned_pdf():
    """Verify graceful handling when PDF has no extractable digital text (scanned image)."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    blank_bytes = buf.getvalue()

    files = {"file": ("scanned_scan.pdf", blank_bytes, "application/pdf")}
    resp = client.post("/api/scanner/analyze-pdf", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert data["status"] == "NO_EXTRACTABLE_TEXT"
    assert data["fallback_available"] is True
    assert "OCR" in data["message"] or "scanned" in data["message"]


def test_pdf_scanner_invalid_file():
    """Verify error handling when a non-PDF file is submitted."""
    files = {"file": ("malicious.exe", b"NOT A PDF FILE DATA", "application/octet-stream")}
    resp = client.post("/api/scanner/analyze-pdf", files=files)
    assert resp.status_code == 422


# ============================================================================
# 3. GOOGLE FORM SCANNER TESTS
# ============================================================================

def test_form_scanner_invalid_url():
    """Verify invalid URL handling for form scanner."""
    resp = client.post("/api/scanner/analyze-form", json={"url": "not-a-valid-url"})
    assert resp.status_code in (200, 422)
    if resp.status_code == 200:
        assert resp.json()["success"] is False


def test_form_scanner_private_or_restricted_form():
    """Verify that private/unreachable Google Forms return graceful message without fabricating."""
    # Using a fake/non-existent Google Form ID that will return 404 or auth challenge
    resp = client.post("/api/scanner/analyze-form", json={"url": "https://docs.google.com/forms/d/e/1FAIpQLSc-NONEXISTENT-TEST-ID-99999/viewform"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["input_type"] == "GOOGLE_FORM"
    assert data["fallback_available"] is True
    assert "Paste" in data["message"] or "access" in data["message"].lower()


def test_form_scanner_direct_pipeline_simulation():
    """
    Test the central risk pipeline on a parsed Google Form data structure
    requesting sensitive Aadhaar and registration fees.
    """
    from app.services.risk_pipeline import run_central_risk_pipeline
    form_text = (
        "Recruitment Form: Online Freelance Data Entry Application\n\n"
        "Description / Overview:\n"
        "Apply for high paying remote vacancies. Earn ₹40,000 monthly.\n\n"
        "Requested Information & Application Fields:\n"
        "1. Full Name\n"
        "2. Upload Aadhaar Card (Front and Back)\n"
        "3. Bank Account Number & IFSC Code\n"
        "4. UPI ID for Registration Fee (₹1,500 mandatory)\n"
        "5. Enter OTP received for verification\n"
    )
    result = run_central_risk_pipeline(
        input_type="GOOGLE_FORM",
        text=form_text,
        url="https://forms.gle/mocktest123",
        title="Online Freelance Data Entry Application"
    )
    assert result["success"] is True
    assert result["input_type"] == "GOOGLE_FORM"
    assert result["risk_score"] >= 80
    assert result["risk_level"] == "CRITICAL"
    assert result["categories"]["financial_risk"]["level"] in ("High", "Critical")
    assert result["categories"]["identity_risk"]["level"] in ("High", "Critical")
    assert len(result["recommendations"]) > 0


# ============================================================================
# 4. REGRESSION TESTS (Existing URL, Content Fallback, Chrome Extension)
# ============================================================================

def test_regression_url_scanner():
    """Verify that the existing POST /api/scan endpoint still functions identically."""
    resp = client.post("/api/scan", json={"url": "https://example.com/"})
    assert resp.status_code == 200
    data = resp.json()
    assert "risk_score" in data
    assert "risk_level" in data
    assert "categories" in data
    assert data["input_type"] == "URL"


def test_regression_browser_fallback_content_scanner():
    """Verify that POST /api/scanner/analyze-content still works with existing format."""
    resp = client.post("/api/scanner/analyze-content", json={
        "url": "https://example.com/job",
        "title": "Software Engineer",
        "company": "Example Inc.",
        "content": "Looking for experienced software engineers with Go and Python experience. Standard hiring."
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_score"] < 40
    assert data["risk_level"] == "LOW"
    assert data["content_analyzed"] is True
    assert "categories" in data


def test_regression_chrome_extension_risk_endpoint():
    """Verify that Chrome extension endpoint POST /api/risk/analyze retains full compatibility."""
    resp = client.post("/api/risk/analyze", json={
        "url": "https://example.com/job",
        "job_text": "Must pay ₹2,000 upfront fee for training kit. WhatsApp recruiter only.",
        "company_name": "Quick Jobs"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["risk_score"] >= 75
    assert data["risk_level"] == "CRITICAL"
    assert "summary" in data
    assert "signals" in data
    assert "categories" in data
    assert "recommendations" in data
