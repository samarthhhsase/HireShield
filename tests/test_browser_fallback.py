import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.scraper import (
    FETCH_BLOCKED,
    BROWSER_CONTENT_RECEIVED,
    BROWSER_PROVIDED,
)

client = TestClient(app)


def test_fallback_1_blocked_url_initial_state():
    """Test 1 — Blocked URL returns 403 -> FETCH_BLOCKED -> Score N/A -> fallback_available = True."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.url = "https://www.naukri.com/job-listings-sr-recruiter-12345"
    mock_response.history = []
    mock_response.text = "<html><body>Access Denied - 403 Forbidden</body></html>"

    with patch("httpx.Client.get", return_value=mock_response):
        response = client.post("/api/scan", json={"url": "https://www.naukri.com/job-listings-sr-recruiter-12345"})
        assert response.status_code == 200
        data = response.json()
        assert data["fetch_status"] == FETCH_BLOCKED
        assert data["http_status"] == 403
        assert data["content_analyzed"] is False
        assert data["fallback_available"] is True
        assert data["risk_score"] is None
        assert data["risk_level"] == "INCOMPLETE"
        assert data["risk_assessment_status"] == "INCOMPLETE"
        assert data["scores"]["behavioral"] is None
        assert data["scores"]["linguistic"] is None
        assert data["scores"]["structural"] is None
        assert data["layers"]["content"]["status"] == "UNAVAILABLE"
        assert data["layers"]["infrastructure"]["status"] == "AVAILABLE"


def test_fallback_2_submit_valid_job_content():
    """Test 2 — Submit valid job content -> 200 -> content analyzed -> NLP executed -> Risk Engine executed."""
    payload = {
        "url": "https://www.naukri.com/job-listings-sr-recruiter-12345",
        "title": "Senior Talent Acquisition Specialist",
        "company": "Enterprise Tech Solutions",
        "content": (
            "We are seeking an experienced Senior Talent Acquisition Specialist to lead our engineering "
            "hiring across distributed teams. Responsibilities include full lifecycle recruiting, collaborating "
            "with engineering managers, and executing hiring strategies. Requires 5+ years technical recruiting "
            "experience, strong communication skills, and proficiency with modern ATS platforms."
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["fetch_status"] == BROWSER_CONTENT_RECEIVED
    assert data["content_analyzed"] is True
    assert data["content_analysis_status"] == "CONTENT_ANALYSIS_AVAILABLE"
    assert data["risk_assessment_status"] == "RISK_ASSESSMENT_COMPLETE"
    assert data["fallback_available"] is False
    assert data["risk_score"] is not None
    assert data["risk_score"] <= 20
    assert data["risk_level"] == "LOW"
    assert data["job"]["title"] == "Senior Talent Acquisition Specialist"
    assert data["job"]["company"] == "Enterprise Tech Solutions"
    assert data["scores"]["behavioral"] == 0
    assert data["scores"]["linguistic"] == 0
    assert data["scores"]["structural"] == 0
    assert data["layers"]["content"]["status"] == "AVAILABLE"
    assert data["layers"]["content"]["source"] == "browser_fallback"
    assert "pipeline_stages" in data
    assert "CONTENT_RECEIVED" in data["pipeline_stages"]
    assert "ANALYSIS_COMPLETE" in data["pipeline_stages"]


def test_fallback_3_empty_and_whitespace_content():
    """Test 3 — Empty or whitespace content returns clean 422 validation error."""
    # Completely empty content
    r1 = client.post(
        "/api/scanner/analyze-content",
        json={"url": "https://example.com/job", "content": ""},
    )
    assert r1.status_code == 422
    assert "empty" in r1.json()["detail"].lower()

    # Whitespace-only content
    r2 = client.post(
        "/api/scanner/analyze-content",
        json={"url": "https://example.com/job", "content": "   \n\t  "},
    )
    assert r2.status_code == 422
    assert "empty" in r2.json()["detail"].lower()

    # Too brief content
    r3 = client.post(
        "/api/scanner/analyze-content",
        json={"url": "https://example.com/job", "content": "short"},
    )
    assert r3.status_code == 422
    assert "too brief" in r3.json()["detail"].lower()


def test_fallback_4_suspicious_sample_detected():
    """Test 4 — Suspicious sample detects fee + Aadhaar/PAN + WhatsApp and triggers critical override."""
    payload = {
        "url": "https://job-offer-portal-xyz.info/apply",
        "title": "URGENT HIRING: Data Entry Operator",
        "company": "Fast Cash Ventures",
        "content": (
            "URGENT HIRING: Immediate joining without interview! 100% guaranteed job placement. "
            "Earn ₹50,000 monthly with no experience required. Mandatory registration fee of ₹1,500 "
            "required as refundable security deposit before onboarding. Please send your Aadhaar card, "
            "PAN card, and bank account details on WhatsApp to +91-9876543210. Limited slots available, "
            "apply within 24 hours to secure placement!!!!!"
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["content_analyzed"] is True
    assert data["risk_score"] >= 85
    assert data["risk_level"] == "CRITICAL"
    assert data["scores"]["behavioral"] >= 45
    assert data["scores"]["linguistic"] >= 25
    assert data["scores"]["structural"] >= 20

    # Verify detected red flags
    flag_messages = " ".join(f["message"].lower() for f in data["red_flags"])
    assert "sensitive identity" in flag_messages
    assert "payment" in flag_messages or "fee" in flag_messages
    assert "urgency" in flag_messages
    assert "informal messaging" in flag_messages


def test_fallback_5_legitimate_sample_no_overfitting():
    """
    Test 5 — Legitimate sample containing words 'salary', 'contact', 'apply', 'urgent'
    must NOT be marked suspicious.
    """
    payload = {
        "url": "https://careers.google.com/jobs/results/12345",
        "title": "Staff Software Engineer",
        "company": "Google LLC",
        "content": (
            "Google is seeking a Staff Software Engineer. In this role you will architect distributed "
            "systems and collaborate across product teams. We have an urgent requirement for engineering "
            "leaders. We offer a competitive salary, comprehensive healthcare, and equity packages. "
            "Please contact our recruitment team or apply now through the careers portal if interested."
        ),
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["content_analyzed"] is True
    # Should have 0 behavioral, 0 linguistic, 0 structural flags
    assert data["scores"]["behavioral"] == 0
    assert data["scores"]["linguistic"] == 0
    assert data["scores"]["structural"] == 0
    assert data["risk_score"] <= 20
    assert data["risk_level"] == "LOW"
    assert len(data["red_flags"]) == 0


def test_fallback_6_content_too_large():
    """Test 6 — Submissions exceeding 100,000 characters are rejected with a clean 422."""
    massive_content = "Word " * 25000  # ~125,000 chars
    response = client.post(
        "/api/scanner/analyze-content",
        json={"url": "https://example.com/job", "content": massive_content},
    )
    assert response.status_code == 422
    assert "maximum limit" in response.json()["detail"].lower()


def test_fallback_7_invalid_url_rejected():
    """Test 7 — Invalid URL string is rejected with a clean 422."""
    response = client.post(
        "/api/scanner/analyze-content",
        json={"url": "ftp://not-a-web-url", "content": "Valid job description content goes here for testing."},
    )
    assert response.status_code == 422
    assert "invalid" in response.json()["detail"].lower()


def test_fallback_8_e2e_regression_flow():
    """
    Test 8 — Complete workflow:
    1. Scan returns 403 -> FETCH_BLOCKED -> INCOMPLETE
    2. Fallback submitted -> BROWSER_CONTENT_RECEIVED -> COMPLETE
    3. Layer A retained + Layer B calculated.
    """
    blocked_url = "https://jobs.apple.com/en-us/details/200684375-1052/integration-engineering-software-engineer"
    mock_403 = MagicMock()
    mock_403.status_code = 403
    mock_403.url = blocked_url
    mock_403.history = []
    mock_403.text = "<html><body>403 Forbidden - Apple WAF</body></html>"

    with patch("httpx.Client.get", return_value=mock_403):
        # 1. URL Scan
        scan_res = client.post("/api/scan", json={"url": blocked_url})
        assert scan_res.status_code == 200
        scan_data = scan_res.json()
        assert scan_data["fetch_status"] == FETCH_BLOCKED
        assert scan_data["risk_score"] is None
        assert scan_data["risk_level"] == "INCOMPLETE"
        assert scan_data["fallback_available"] is True

        # Layer A is populated
        assert scan_data["layers"]["infrastructure"]["status"] == "AVAILABLE"
        assert scan_data["url_intelligence"]["domain"] is not None

        # 2. Browser Content Fallback
        fallback_res = client.post(
            "/api/scanner/analyze-content",
            json={
                "url": scan_data["url"],
                "title": "Integration Engineering Software Engineer",
                "company": "Apple Inc.",
                "content": (
                    "Apple is seeking an Integration Engineering Software Engineer to join our CoreOS team. "
                    "You will develop automated testing frameworks, CI/CD infrastructure, and regression verification "
                    "across macOS and iOS architectures. Requires BS/MS in Computer Science, 4+ years of C++, Python, "
                    "and distributed systems experience. Competitive compensation and comprehensive benefits."
                ),
            },
        )
        assert fallback_res.status_code == 200
        fallback_data = fallback_res.json()

        # State transition confirmed
        assert fallback_data["fetch_status"] == BROWSER_CONTENT_RECEIVED
        assert fallback_data["content_analyzed"] is True
        assert fallback_data["risk_score"] is not None
        assert fallback_data["risk_level"] == "LOW"
        assert fallback_data["risk_assessment_status"] == "RISK_ASSESSMENT_COMPLETE"

        # Layer A retained
        assert fallback_data["layers"]["infrastructure"]["status"] == "AVAILABLE"
        assert fallback_data["url_intelligence"]["domain"] == "jobs.apple.com"

        # Layer B evaluated
        assert fallback_data["layers"]["content"]["status"] == "AVAILABLE"
        assert fallback_data["layers"]["content"]["source"] == "browser_fallback"
        assert fallback_data["scores"]["behavioral"] is not None
        assert fallback_data["scores"]["linguistic"] is not None
        assert fallback_data["scores"]["structural"] is not None
