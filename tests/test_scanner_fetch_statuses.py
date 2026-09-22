import pytest
from unittest.mock import patch, MagicMock
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.services.scraper import (
    FETCH_SUCCESS,
    FETCH_BLOCKED,
    FETCH_NOT_FOUND,
    FETCH_RATE_LIMITED,
    FETCH_TIMEOUT,
    FETCH_INVALID_URL,
    BROWSER_PROVIDED,
)

client = TestClient(app)


def test_1_successful_page_200():
    """Test 1 — Successful page: 200 -> FETCH_SUCCESS -> content analyzed -> Risk Engine executed."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.url = "https://example.com/careers/engineer"
    mock_response.history = []
    mock_response.text = "<html><head><title>Backend Engineer at TechCorp</title></head><body>We are hiring a backend engineer with Python skills.</body></html>"

    with patch("httpx.Client.get", return_value=mock_response):
        response = client.post("/api/scan", json={"url": "https://example.com/careers/engineer"})
        assert response.status_code == 200
        data = response.json()
        assert data["fetch_status"] == FETCH_SUCCESS
        assert data["http_status"] == 200
        assert data["content_analyzed"] is True
        assert data["fallback_available"] is False
        assert data["risk_score"] >= 0
        assert "Backend Engineer" in data["job"]["title"]


def test_2_apple_style_blocked_page_403():
    """Test 2 — Apple-style blocked page: 403 -> FETCH_BLOCKED -> INCOMPLETE risk assessment -> fallback_available = true."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.url = "https://jobs.apple.com/en-us/details/200684375-1052/integration-engineering-software-engineer?team=SFTWR"
    mock_response.history = []
    mock_response.text = "<html><body>Access Denied - 403 Forbidden</body></html>"

    with patch("httpx.Client.get", return_value=mock_response):
        response = client.post("/api/scan", json={"url": "https://jobs.apple.com/en-us/details/200684375-1052/integration-engineering-software-engineer?team=SFTWR"})
        assert response.status_code == 200
        data = response.json()
        assert data["fetch_status"] == FETCH_BLOCKED
        assert data["http_status"] == 403
        assert data["content_analyzed"] is False
        assert data["fallback_available"] is True
        assert data["risk_impact"] == 0
        # A 403 is NOT fraud, but also NOT 0 / LOW risk: it is an INCOMPLETE assessment!
        assert data["risk_level"] == "INCOMPLETE"
        assert data["risk_score"] is None
        assert data["risk_assessment_status"] == "INCOMPLETE"
        assert data["scores"]["behavioral"] is None
        assert data["scores"]["linguistic"] is None
        assert data["scores"]["structural"] is None
        assert data["scores"]["technical"] is not None
        assert data["layers"]["infrastructure"]["status"] == "AVAILABLE"
        assert data["layers"]["content"]["status"] == "UNAVAILABLE"
        assert data["red_flags"] == []
        assert "403" in data["message"]


def test_3_not_found_page_404():
    """Test 3 — Not found: 404 -> FETCH_NOT_FOUND -> INCOMPLETE assessment."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.url = "https://example.com/expired-job"
    mock_response.history = []
    mock_response.text = "<html><body>404 Not Found</body></html>"

    with patch("httpx.Client.get", return_value=mock_response):
        response = client.post("/api/scan", json={"url": "https://example.com/expired-job"})
        assert response.status_code == 200
        data = response.json()
        assert data["fetch_status"] == FETCH_NOT_FOUND
        assert data["http_status"] == 404
        assert data["content_analyzed"] is False
        assert data["fallback_available"] is True
        assert data["risk_level"] == "INCOMPLETE"
        assert data["risk_score"] is None
        assert data["risk_assessment_status"] == "INCOMPLETE"


def test_4_rate_limiting_429():
    """Test 4 — Rate limiting: 429 -> FETCH_RATE_LIMITED."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.url = "https://example.com/jobs"
    mock_response.history = []
    mock_response.text = "<html><body>Too Many Requests</body></html>"

    with patch("httpx.Client.get", return_value=mock_response):
        response = client.post("/api/scan", json={"url": "https://example.com/jobs"})
        assert response.status_code == 200
        data = response.json()
        assert data["fetch_status"] == FETCH_RATE_LIMITED
        assert data["http_status"] == 429
        assert data["content_analyzed"] is False
        assert data["fallback_available"] is True


def test_5_timeout_handling():
    """Test 5 — Timeout: timeout -> FETCH_TIMEOUT."""
    with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Connection timed out")):
        response = client.post("/api/scan", json={"url": "https://slow-remote-site.com/job"})
        assert response.status_code == 200
        data = response.json()
        assert data["fetch_status"] == FETCH_TIMEOUT
        assert data["content_analyzed"] is False
        assert data["fallback_available"] is True
        assert "timed out" in data["message"]


def test_6_invalid_url():
    """Test 6 — Invalid URL: invalid URL -> FETCH_INVALID_URL."""
    response = client.post("/api/scan", json={"url": "not-a-valid-url-at-all"})
    assert response.status_code == 200
    data = response.json()
    assert data["fetch_status"] == FETCH_INVALID_URL
    assert data["content_analyzed"] is False
    assert data["fallback_available"] is False


def test_7_browser_content_fallback():
    """Test 7 — Browser content: Send sample job content to POST /api/scanner/analyze-content."""
    payload = {
        "url": "https://jobs.apple.com/en-us/details/200684375-1052/integration-engineering-software-engineer?team=SFTWR",
        "title": "Integration Engineering Software Engineer",
        "company": "Apple Inc.",
        "content": "Join Apple's CoreOS team. You will be responsible for continuous integration, regression testing, and verification across macOS and iOS architectures. Requires 4+ years of C++, Python, and distributed systems."
    }
    response = client.post("/api/scanner/analyze-content", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["fetch_status"] == BROWSER_PROVIDED
    assert data["content_analyzed"] is True
    assert data["job"]["title"] == "Integration Engineering Software Engineer"
    assert data["job"]["company"] == "Apple Inc."
    assert data["content_intelligence"]["status"] == "ANALYZED"
    assert data["content_intelligence"]["source"] == "browser_fallback"
    assert data["risk_score"] <= 20
    assert data["risk_level"] == "LOW"


def test_8_apple_regression_url():
    """Test 8 — Apple regression test: URL must return 200 with structured data and NOT high risk."""
    apple_url = "https://jobs.apple.com/en-us/details/200684375-1052/integration-engineering-software-engineer?team=SFTWR"
    response = client.post("/api/scan", json={"url": apple_url})
    assert response.status_code == 200
    data = response.json()
    assert data["fetch_status"] in (FETCH_SUCCESS, FETCH_BLOCKED)
    if data["fetch_status"] == FETCH_BLOCKED:
        assert data["risk_level"] == "INCOMPLETE"
        assert data["risk_score"] is None
        assert data["content_analyzed"] is False
    else:
        assert data["risk_level"] == "LOW"
        assert data["content_analyzed"] is True
    assert data["red_flags"] == []
    assert data["technical_checks"]["dns_exists"] is True
    assert data["technical_checks"]["ssl_valid"] is True
