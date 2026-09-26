import os
import time
import json
import base64
import hmac
import hashlib
import secrets
import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User

logger = logging.getLogger("hireshield.auth")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv("AUTH_SECRET_KEY") or "hireshield-cyber-intel-secret-key-2026-v1"
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

security_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash a plaintext password using PBKDF2-HMAC-SHA256 with 100,000 iterations."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    )
    return f"pbkdf2_sha256${salt}${key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a plaintext password against the stored PBKDF2 hash."""
    try:
        parts = stored_hash.split("$")
        if len(parts) != 3 or parts[0] != "pbkdf2_sha256":
            return False
        salt = parts[1]
        expected_key_hex = parts[2]
        computed_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,
        )
        return secrets.compare_digest(computed_key.hex(), expected_key_hex)
    except Exception as exc:
        logger.error(f"Password verification error: {exc}")
        return False


def create_access_token(user_id: str, email: str, role: str = "Lead Security Analyst") -> str:
    """Generate a tamper-proof HMAC-SHA256 signed bearer access token with expiration."""
    exp_time = int(time.time()) + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": exp_time,
        "iat": int(time.time()),
    }
    payload_json = json.dumps(payload, separators=(",", ":"))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8").rstrip("=")

    signature = hmac.new(
        JWT_SECRET_KEY.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"hs_{payload_b64}.{signature}"


def verify_access_token(token: str) -> Optional[dict]:
    """Verify signature and expiration of an access token."""
    try:
        if not token:
            return None

        # Support both 'hs_' prefixed tokens and standard tokens
        raw_token = token
        if raw_token.startswith("Bearer "):
            raw_token = raw_token[7:].strip()
        if raw_token.startswith("hs_"):
            raw_token = raw_token[3:].strip()

        parts = raw_token.split(".")
        if len(parts) == 2:
            payload_b64, signature = parts
            expected_sig = hmac.new(
                JWT_SECRET_KEY.encode("utf-8"),
                payload_b64.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()

            if not secrets.compare_digest(signature, expected_sig):
                return None

            padding = "=" * ((4 - len(payload_b64) % 4) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
            payload = json.loads(payload_bytes.decode("utf-8"))

            if payload.get("exp", 0) < time.time():
                return None

            return payload
        elif len(parts) == 3:
            # Standard RFC 7519 3-segment format: header.payload.signature
            header_b64, payload_b64, signature = parts
            signed_content = f"{header_b64}.{payload_b64}".encode("utf-8")
            expected_sig_hex = hmac.new(
                JWT_SECRET_KEY.encode("utf-8"),
                signed_content,
                hashlib.sha256,
            ).hexdigest()
            # Also check base64url signature
            expected_sig_b64 = base64.urlsafe_b64encode(
                hmac.new(JWT_SECRET_KEY.encode("utf-8"), signed_content, hashlib.sha256).digest()
            ).decode("utf-8").rstrip("=")

            if not (secrets.compare_digest(signature, expected_sig_hex) or secrets.compare_digest(signature, expected_sig_b64)):
                return None

            padding = "=" * ((4 - len(payload_b64) % 4) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
            payload = json.loads(payload_bytes.decode("utf-8"))

            if payload.get("exp", 0) < time.time():
                return None

            return payload

        return None
    except Exception as exc:
        logger.warning(f"Failed to verify access token: {exc}")
        return None


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency to extract and authenticate the current user via Bearer token."""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_access_token(auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired security token. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub") or payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The security analyst profile is either inactive or no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    FastAPI dependency to optionally authenticate user via Bearer token.
    - If no Authorization header is present: returns None.
    - If an invalid or expired token is presented: raises 401 so caller can handle session expiry.
    - If valid: returns the authenticated User instance.
    """
    if not auth or not auth.credentials:
        return None

    payload = verify_access_token(auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session has expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub") or payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def seed_default_analyst(db: Session):
    """Seed the default analyst credential (analyst@hireshield.ai / Password123!)."""
    default_email = "analyst@hireshield.ai"
    existing = db.query(User).filter(User.email == default_email).first()
    if not existing:
        analyst = User(
            id="USR-SEC-DEFAULT-01",
            full_name="Lead Security Analyst",
            email=default_email,
            password_hash=hash_password("Password123!"),
            organization="HireShield Cyber Intelligence",
            role="Lead Security Analyst",
            is_active=True,
        )
        db.add(analyst)
        db.commit()
        logger.info(f"Default analyst account seeded: {default_email}")
