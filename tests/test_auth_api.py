import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import hash_password, verify_password, create_access_token, verify_access_token

client = TestClient(app)


def test_password_hashing_and_verification():
    password = "SuperSecretPassword2026!"
    hashed = hash_password(password)
    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_token_creation_and_verification():
    token = create_access_token("usr-123", "test@hireshield.ai", "Security Analyst")
    assert token.startswith("hs_")
    
    payload = verify_access_token(token)
    assert payload is not None
    assert payload["sub"] == "usr-123"
    assert payload["email"] == "test@hireshield.ai"
    assert payload["role"] == "Security Analyst"


def test_default_analyst_login():
    response = client.post(
        "/api/auth/login",
        json={"email": "analyst@hireshield.ai", "password": "Password123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "analyst@hireshield.ai"
    assert data["user"]["name"] == "Lead Security Analyst"


def test_invalid_login_credentials():
    response = client.post(
        "/api/auth/login",
        json={"email": "analyst@hireshield.ai", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    assert "Invalid analyst email or security password." in response.json()["detail"]


def test_register_and_get_me():
    new_email = f"analyst.test.{id(test_register_and_get_me)}@hireshield.ai"
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Matrix",
            "email": new_email,
            "password": "JanePassword123!",
            "role": "Threat Intelligence Officer"
        }
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    token = reg_data["access_token"]
    assert reg_data["user"]["email"] == new_email

    # Verify /api/auth/me with bearer token
    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["name"] == "Jane Matrix"
    assert me_data["email"] == new_email
    assert me_data["role"] == "Threat Intelligence Officer"


def test_unauthorized_get_me():
    response = client.get("/api/auth/me")
    assert response.status_code == 401
