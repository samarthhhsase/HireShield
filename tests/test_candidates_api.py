import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal, Base, engine
from app.models.candidate import Candidate
from app.services.candidate_service import seed_default_candidates

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_default_candidates(db)
    yield


def test_list_candidates_returns_seeded_data():
    response = client.get("/api/candidates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    # Check structure of first item
    item = data[0]
    assert "id" in item
    assert "candidateName" in item or "candidate_name" in item
    assert "risk_score" in item
    assert "risk_level" in item
    assert "scores" in item
    assert "technical_checks" in item
    assert "verification_audit" in item


def test_get_candidate_by_valid_id():
    response = client.get("/api/candidates/HS-2026-00421")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "HS-2026-00421"
    assert "Alex Mercer" in (data.get("candidateName") or "")
    assert data["risk_score"] == 11
    assert data["risk_level"] == "LOW"
    assert data["verdict"] == "VERIFIED_LEGITIMATE"


def test_get_candidate_by_invalid_id_returns_404():
    response = client.get("/api/candidates/HS-NON-EXISTENT-999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_and_delete_candidate():
    payload = {
        "candidate_name": "Test Candidate Engineer",
        "title": "Senior Security Threat Analyst",
        "company": "HireShield Labs",
        "url": "https://hireshield-test-target.org/job/1",
        "risk_score": 15,
        "risk_level": "LOW",
        "verdict": "VERIFIED_LEGITIMATE",
        "scores": {"behavioral": 10, "linguistic": 5, "structural": 0, "technical": 10},
        "red_flags": [],
        "green_flags": [{"message": "Verified corporate domain"}],
    }
    # Create
    create_res = client.post("/api/candidates", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["title"] == "Senior Security Threat Analyst"
    assert created["company"] == "HireShield Labs"
    target_id = created["id"]

    # Retrieve
    get_res = client.get(f"/api/candidates/{target_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == target_id

    # Delete
    del_res = client.delete(f"/api/candidates/{target_id}")
    assert del_res.status_code == 200

    # Retrieve again should 404
    get_again = client.get(f"/api/candidates/{target_id}")
    assert get_again.status_code == 404


def test_jobs_alias_endpoints():
    # /api/jobs should return the same list
    res = client.get("/api/jobs")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # /api/jobs/{id}
    res_single = client.get("/api/jobs/HS-2026-00421")
    assert res_single.status_code == 200
    assert res_single.json()["id"] == "HS-2026-00421"


def test_filter_candidates_by_risk_level():
    res = client.get("/api/candidates?risk_level=CRITICAL")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 1
    for item in items:
        assert item["risk_level"] == "CRITICAL"


def test_content_scan_auto_persists_in_candidates():
    payload = {
        "title": "Crypto Arbitrage Specialist",
        "company": "Moonshot Vault",
        "url": "https://moonshot-vault-fake.xyz/apply",
        "content": "Immediate opening for remote crypto trader! Pay $100 registration fee to begin training immediately.",
    }
    scan_res = client.post("/api/scanner/analyze-content", json=payload)
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert "id" in scan_data

    # Verify that the scan is now present in GET /api/candidates
    list_res = client.get("/api/candidates")
    assert list_res.status_code == 200
    candidate_ids = [c["id"] for c in list_res.json()]
    assert scan_data["id"] in candidate_ids

    # Verify single lookup
    single_res = client.get(f"/api/candidates/{scan_data['id']}")
    assert single_res.status_code == 200
    assert single_res.json()["title"] == "Crypto Arbitrage Specialist"


def test_reports_endpoint():
    res = client.get("/api/reports")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    report = data[0]
    assert "report_id" in report
    assert "status" in report
    assert report["status"] == "COMPILED"


def test_activity_endpoint():
    res = client.get("/api/activity")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    event = data[0]
    assert "id" in event
    assert "timestamp" in event
    assert "endpoint" in event
    assert event["endpoint"] == "/api/scan"
    assert event["status"] == 200


