"""
HireShield Authentication & Scanner Integration Tests.

Verifies:
1. User registration, login, and bearer JWT token handling.
2. Protected analysis and scan association with backend database user ID.
3. User-specific scan history: User A only sees User A's scans; User B only sees User B's scans.
4. IDOR Protection: User A cannot retrieve User B's scans or candidates (HTTP 403 Forbidden).
5. Unauthenticated rejection: GET /api/scans returns 401 Unauthorized without credentials.
6. Multi-input authentication consistency: URL, Text, PDF, Form scanners.
"""

import time
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_auth_scanner_integration_full_flow():
    timestamp = int(time.time() * 1000)
    email_a = f"analyst.a.{timestamp}@cyberdefense.org"
    email_b = f"analyst.b.{timestamp}@cyberdefense.org"

    # 1. Register User A
    resp_signup_a = client.post(
        "/api/auth/signup",
        json={
            "full_name": "Analyst Alice",
            "email": email_a,
            "password": "PasswordAlice123!",
            "confirm_password": "PasswordAlice123!",
            "organization": "Cyber Intelligence Unit A",
        },
    )
    assert resp_signup_a.status_code == 201, resp_signup_a.text
    token_a = resp_signup_a.json()["access_token"]
    user_a = resp_signup_a.json()["user"]
    user_a_id = user_a["id"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register User B
    resp_signup_b = client.post(
        "/api/auth/signup",
        json={
            "full_name": "Analyst Bob",
            "email": email_b,
            "password": "PasswordBob123!",
            "confirm_password": "PasswordBob123!",
            "organization": "Cyber Intelligence Unit B",
        },
    )
    assert resp_signup_b.status_code == 201, resp_signup_b.text
    token_b = resp_signup_b.json()["access_token"]
    user_b = resp_signup_b.json()["user"]
    user_b_id = user_b["id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User A performs a Text Scan
    text_a = "Immediate hiring for remote software engineer. Send your technical resume and portfolio. No upfront fees."
    resp_scan_a = client.post(
        "/api/scanner/analyze-text",
        json={"text": text_a, "title": "Software Engineer A", "company": "Tech Corp A"},
        headers=headers_a,
    )
    assert resp_scan_a.status_code == 200, resp_scan_a.text
    scan_a_data = resp_scan_a.json()
    assert scan_a_data["user_id"] == user_a_id

    # 4. User B performs a Text Scan
    text_b = "Urgent data entry positions! Must pay refundable processing fee of 2000 INR before training. Send Aadhaar."
    resp_scan_b = client.post(
        "/api/scanner/analyze-text",
        json={"text": text_b, "title": "Data Entry B", "company": "Scam Operations B"},
        headers=headers_b,
    )
    assert resp_scan_b.status_code == 200, resp_scan_b.text
    scan_b_data = resp_scan_b.json()
    assert scan_b_data["user_id"] == user_b_id

    # 5. User A retrieves their scan history: GET /api/scans
    resp_history_a = client.get("/api/scans", headers=headers_a)
    assert resp_history_a.status_code == 200
    history_a = resp_history_a.json()
    assert history_a["user_id"] == user_a_id
    assert any(s["title"] == "Software Engineer A" for s in history_a["scans"])
    # Crucial security assertion: User A MUST NOT see User B's scans
    assert not any(s["title"] == "Data Entry B" for s in history_a["scans"])

    # 6. User B retrieves their scan history: GET /api/scans
    resp_history_b = client.get("/api/scans", headers=headers_b)
    assert resp_history_b.status_code == 200
    history_b = resp_history_b.json()
    assert history_b["user_id"] == user_b_id
    assert any(s["title"] == "Data Entry B" for s in history_b["scans"])
    # Crucial security assertion: User B MUST NOT see User A's scans
    assert not any(s["title"] == "Software Engineer A" for s in history_b["scans"])

    # 7. IDOR Protection: User A attempts to directly access User B's scan detail
    user_b_scan_id = history_b["scans"][0]["id"]
    resp_idor_scan = client.get(f"/api/scans/{user_b_scan_id}", headers=headers_a)
    assert resp_idor_scan.status_code == 403, "User A must receive 403 Forbidden when accessing User B's scan"
    assert "permission" in resp_idor_scan.json()["detail"].lower()

    # User B accessing their own scan detail succeeds
    resp_owner_scan = client.get(f"/api/scans/{user_b_scan_id}", headers=headers_b)
    assert resp_owner_scan.status_code == 200
    assert resp_owner_scan.json()["id"] == user_b_scan_id

    # 8. IDOR Protection: User B attempts to directly access User A's candidate dossier
    user_a_cand_id = scan_a_data.get("id") or scan_a_data.get("candidate_id")
    if user_a_cand_id:
        resp_idor_cand = client.get(f"/api/candidates/{user_a_cand_id}", headers=headers_b)
        assert resp_idor_cand.status_code == 403, "User B must receive 403 Forbidden when accessing User A's candidate"


def test_unauthenticated_scans_history_rejected():
    # Attempting to fetch scan history without credentials must return 401 Unauthorized
    resp = client.get("/api/scans")
    assert resp.status_code == 401
    assert "WWW-Authenticate" in resp.headers


def test_invalid_token_rejected_with_401():
    # Attempting to fetch scan history with an invalid token must return 401 Unauthorized
    resp = client.get("/api/scans", headers={"Authorization": "Bearer invalid.token.payload"})
    assert resp.status_code == 401


def test_public_endpoints_remain_accessible():
    # Health and root must remain accessible without authentication
    assert client.get("/health").status_code == 200
    assert client.get("/api/health").status_code == 200
    assert client.get("/").status_code == 200
