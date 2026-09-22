import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import hash_password, create_access_token, verify_access_token

client = TestClient(app)


def test_signup_valid_account_success():
    email = f"analyst.success.{int(time.time()*1000)}@cyberdefense.org"
    response = client.post(
        "/api/auth/signup",
        json={
            "full_name": "Marcus Vance",
            "email": email,
            "password": "CyberShield2026!",
            "confirm_password": "CyberShield2026!",
            "organization": "Vance Defense Systems",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["message"] == "Account created successfully."
    user = data["user"]
    assert user["full_name"] == "Marcus Vance"
    assert user["email"] == email
    assert user["organization"] == "Vance Defense Systems"
    # Security requirement: Never return password, password_hash, or secret
    assert "password" not in user
    assert "password_hash" not in user
    assert "hashed_password" not in user


def test_signup_duplicate_email_rejected():
    email = f"analyst.dup.{int(time.time()*1000)}@cyberdefense.org"
    payload = {
        "full_name": "Elena Rostova",
        "email": email,
        "password": "SecurityPass123!",
        "confirm_password": "SecurityPass123!",
    }
    # First signup
    r1 = client.post("/api/auth/signup", json=payload)
    assert r1.status_code == 201

    # Second signup with same email
    r2 = client.post("/api/auth/signup", json=payload)
    assert r2.status_code == 400
    assert r2.json()["detail"] == "An account with this email already exists."


def test_signup_invalid_email_rejected():
    response = client.post(
        "/api/auth/signup",
        json={
            "full_name": "Test User",
            "email": "not-a-valid-email",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    assert response.status_code == 422


def test_signup_weak_password_rejected():
    # Less than 8 chars
    r1 = client.post(
        "/api/auth/signup",
        json={
            "full_name": "Weak Pass",
            "email": "weak1@example.com",
            "password": "Pass1",
            "confirm_password": "Pass1",
        },
    )
    assert r1.status_code == 422

    # No number
    r2 = client.post(
        "/api/auth/signup",
        json={
            "full_name": "Weak Pass",
            "email": "weak2@example.com",
            "password": "PasswordNoNumber",
            "confirm_password": "PasswordNoNumber",
        },
    )
    assert r2.status_code == 422

    # No uppercase
    r3 = client.post(
        "/api/auth/signup",
        json={
            "full_name": "Weak Pass",
            "email": "weak3@example.com",
            "password": "lowercase12345",
            "confirm_password": "lowercase12345",
        },
    )
    assert r3.status_code == 422


def test_signup_password_mismatch_rejected():
    response = client.post(
        "/api/auth/signup",
        json={
            "full_name": "Mismatch User",
            "email": "mismatch@example.com",
            "password": "Security123!",
            "confirm_password": "DifferentPassword123!",
        },
    )
    assert response.status_code == 422


def test_login_success_and_failures():
    email = f"analyst.login.{int(time.time()*1000)}@cyberdefense.org"
    client.post(
        "/api/auth/signup",
        json={
            "full_name": "Agent Smith",
            "email": email,
            "password": "CorrectPassword99!",
            "confirm_password": "CorrectPassword99!",
            "organization": "Matrix Security",
        },
    )

    # 1. Correct credentials -> success
    r_success = client.post("/api/auth/login", json={"email": email, "password": "CorrectPassword99!"})
    assert r_success.status_code == 200
    data = r_success.json()
    assert "access_token" in data
    assert data["user"]["email"] == email
    assert data["user"]["full_name"] == "Agent Smith"

    # 2. Wrong password -> rejected 401
    r_wrong = client.post("/api/auth/login", json={"email": email, "password": "WrongPassword99!"})
    assert r_wrong.status_code == 401

    # 3. Unknown email -> rejected 401
    r_unknown = client.post("/api/auth/login", json={"email": "nonexistent@unknown.com", "password": "Password123!"})
    assert r_unknown.status_code == 401


def test_jwt_authentication_valid_invalid_expired():
    email = f"analyst.jwt.{int(time.time()*1000)}@cyberdefense.org"
    signup_res = client.post(
        "/api/auth/signup",
        json={
            "full_name": "Token Tester",
            "email": email,
            "password": "CyberToken2026!",
            "confirm_password": "CyberToken2026!",
        },
    )
    valid_token = signup_res.json()["access_token"]

    # 1. Valid JWT -> accessible
    r_valid = client.get("/api/auth/me", headers={"Authorization": f"Bearer {valid_token}"})
    assert r_valid.status_code == 200
    profile = r_valid.json()
    assert profile["email"] == email
    assert profile["full_name"] == "Token Tester"
    assert "password_hash" not in profile

    # 2. Missing JWT -> 401
    r_missing = client.get("/api/auth/me")
    assert r_missing.status_code == 401

    # 3. Invalid JWT -> 401
    r_invalid = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.fake.token"})
    assert r_invalid.status_code == 401

    # 4. Tampered JWT signature -> 401
    tampered_token = valid_token[:-4] + "xxxx"
    r_tampered = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tampered_token}"})
    assert r_tampered.status_code == 401
