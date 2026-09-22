def test_health_endpoint(client):
    """Verify GET /api/health returns status ok and service name."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "HireShield Backend"
