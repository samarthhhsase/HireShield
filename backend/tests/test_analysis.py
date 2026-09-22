def test_analysis_workflow_clean_candidate(client):
    # Register clean candidate
    cand_payload = {
        "name": "Elena Rostova",
        "email": "elena.rostova@techcorp.io",
        "role": "Senior Cloud Architect",
        "resume_text": "Experienced cloud architect with 8 years designing secure Kubernetes clusters on AWS and GCP.",
        "skills": ["aws", "kubernetes", "docker", "python", "terraform"],
        "experience_years": 8.0,
        "job_description": "We are seeking a Senior Cloud Architect with AWS, Kubernetes, and Python experience.",
    }
    c_res = client.post("/api/candidates", json=cand_payload)
    assert c_res.status_code == 201
    cand_id = c_res.json()["id"]

    # Execute Analysis
    anl_res = client.post(f"/api/analysis/{cand_id}")
    assert anl_res.status_code == 200
    data = anl_res.json()

    assert data["candidate_id"] == cand_id
    assert data["candidate_name"] == "Elena Rostova"
    assert data["risk_level"] == "LOW"
    assert 0 <= data["risk_score"] <= 24
    assert "explanation" in data
    assert "breakdown" in data
    assert "signals" in data


def test_analysis_workflow_flagged_candidate(client):
    # Register candidate with fee and urgency patterns
    cand_payload = {
        "name": "Suspicious Recruiter Front",
        "email": "quickhire@suspicious-jobs.net",
        "role": "Remote Data Entry Lead",
        "resume_text": "Immediate urgent hiring! 100% guaranteed job offer. Candidate must submit ₹2000 registration fee and Aadhaar Card for identity verification.",
        "skills": ["typing"],
        "experience_years": 0.5,
        "job_description": "Senior Software Architect with Kubernetes and Docker.",
    }
    c_res = client.post("/api/candidates", json=cand_payload)
    assert c_res.status_code == 201
    cand_id = c_res.json()["id"]

    # Execute Analysis
    anl_res = client.post(f"/api/analysis/{cand_id}")
    assert anl_res.status_code == 200
    data = anl_res.json()

    assert data["risk_score"] >= 50
    assert data["risk_level"] in ["HIGH", "CRITICAL"]
    assert len(data["signals"]) >= 2
    # Verify financial signal was captured
    signal_names = [s["signal_name"] for s in data["signals"]]
    assert "FINANCIAL_OR_CREDENTIAL_SOLICITATION" in signal_names


def test_analysis_candidate_not_found(client):
    res = client.post("/api/analysis/NON-EXISTENT-ID")
    assert res.status_code == 404
    assert res.json()["error"] is True


def test_dashboard_apis(client):
    # Create candidate and run analysis
    cand_payload = {
        "name": "Marcus Vance",
        "email": "marcus@vance.ai",
        "role": "Data Scientist",
        "resume_text": "Machine learning researcher with 4 years experience.",
        "skills": ["python", "machine learning"],
    }
    cand = client.post("/api/candidates", json=cand_payload).json()
    client.post(f"/api/analysis/{cand['id']}")

    # Check Summary
    summary = client.get("/api/dashboard/summary").json()
    assert summary["total_candidates"] >= 1
    assert summary["analyses_completed"] >= 1

    # Check Risk Distribution
    dist = client.get("/api/dashboard/risk-distribution").json()
    assert "low" in dist
    assert "critical" in dist

    # Check Recent Analyses
    recent = client.get("/api/dashboard/recent").json()
    assert len(recent) >= 1
    assert recent[0]["candidate_id"] == cand["id"]
