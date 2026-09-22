import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal, Base, engine
from app.services.candidate_service import seed_default_candidates

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_default_candidates(db)
    yield


def test_extension_score_preserved_in_full_analysis():
    # 1. Simulate Chrome extension calling POST /api/risk/analyze with extracted DOM content
    extension_payload = {
        "url": "https://careers.google.com/jobs/results/senior-security-engineer",
        "company_name": "Google LLC",
        "job_text": "We are seeking a Senior Security Engineer to design distributed zero-trust systems. Competitive compensation, comprehensive health benefits, 401k match. No upfront fees.",
        "recruiter_email": "recruiting-team@google.com",
        "salary": "$185,000 - $240,000 per year",
        "source": "direct",
    }

    resp1 = client.post("/api/risk/analyze", json=extension_payload)
    assert resp1.status_code == 200
    ext_data = resp1.json()

    ext_score = ext_data["risk_score"]
    ext_id = ext_data.get("id")
    assert ext_id is not None, "Extension scan response must contain persistent candidate dossier ID"

    # 2. Simulate web app loading candidate by ID (when 'VIEW FULL ANALYSIS' is clicked)
    resp2 = client.get(f"/api/candidates/{ext_id}")
    assert resp2.status_code == 200
    dossier = resp2.json()

    assert dossier["id"] == ext_id
    assert dossier["risk_score"] == ext_score, f"Expected full analysis score {dossier['risk_score']} to match extension score {ext_score}"
    assert dossier["content_analyzed"] is True
    assert dossier["risk_level"] == ext_data["risk_level"]

