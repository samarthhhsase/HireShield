def test_create_candidate_success(client):
    payload = {
        "name": "Sarah Connor",
        "email": "sarah.connor@cyberdyne.com",
        "phone": "+1-555-0199",
        "role": "Security Operations Lead",
        "resume_text": "10 years defending distributed infrastructure against automated threats.",
        "skills": ["python", "docker", "kubernetes", "incident response"],
        "experience_years": 10.0,
        "education": "B.S. in Computer Science",
        "job_description": "Seeking lead security engineer with Python and Docker experience.",
    }
    response = client.post("/api/candidates", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sarah Connor"
    assert data["email"] == "sarah.connor@cyberdyne.com"
    assert data["id"].startswith("CAND-")
    assert "created_at" in data


def test_create_candidate_duplicate_email(client):
    payload = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "role": "Software Engineer",
    }
    res1 = client.post("/api/candidates", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/candidates", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["message"]


def test_create_candidate_validation_error(client):
    # Invalid email and missing required role
    payload = {
        "name": "J",
        "email": "invalid-email-format",
    }
    response = client.post("/api/candidates", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"] is True
    assert len(data["details"]) > 0


def test_get_and_list_candidates(client):
    payload1 = {"name": "Candidate One", "email": "one@example.com", "role": "Backend Dev"}
    payload2 = {"name": "Candidate Two", "email": "two@example.com", "role": "Frontend Dev"}
    c1 = client.post("/api/candidates", json=payload1).json()
    c2 = client.post("/api/candidates", json=payload2).json()

    # List all
    res = client.get("/api/candidates")
    assert res.status_code == 200
    candidates = res.json()
    assert len(candidates) == 2

    # Get single
    res_single = client.get(f"/api/candidates/{c1['id']}")
    assert res_single.status_code == 200
    assert res_single.json()["email"] == "one@example.com"


def test_update_and_delete_candidate(client):
    payload = {"name": "Alex Mercer", "email": "alex@example.com", "role": "DevOps"}
    created = client.post("/api/candidates", json=payload).json()
    cand_id = created["id"]

    # Update role
    res_update = client.put(f"/api/candidates/{cand_id}", json={"role": "Senior DevOps Lead"})
    assert res_update.status_code == 200
    assert res_update.json()["role"] == "Senior DevOps Lead"

    # Delete
    res_delete = client.delete(f"/api/candidates/{cand_id}")
    assert res_delete.status_code == 204

    # Verify not found
    res_get = client.get(f"/api/candidates/{cand_id}")
    assert res_get.status_code == 404
