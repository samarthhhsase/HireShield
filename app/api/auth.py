import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    RegisterRequest,
    AuthResponse,
    UserProfileResponse,
)
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

logger = logging.getLogger("hireshield.api.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Enroll a new Security Analyst with persistent credentials in SQLite."""
    normalized_email = str(request.email).lower().strip()

    # Check for existing email duplicate
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Hash password and persist user
    new_user = User(
        first_name=request.first_name.strip() if request.first_name else None,
        second_name=request.second_name.strip() if request.second_name else None,
        full_name=request.full_name.strip(),
        email=normalized_email,
        password_hash=hash_password(request.password),
        organization=request.organization.strip() if request.organization else None,
        role=request.role or "Security Analyst",
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Signed up new user: {new_user.email} (ID: {new_user.id})")

    # Generate token
    token = create_access_token(new_user.id, new_user.email, new_user.role)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfileResponse(**new_user.to_dict()),
        message="Account created successfully.",
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Backward-compatible register endpoint."""
    normalized_email = str(request.email).lower().strip()

    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    new_user = User(
        full_name=request.name.strip(),
        email=normalized_email,
        password_hash=hash_password(request.password),
        organization=request.organization.strip() if request.organization else None,
        role=request.role or "Security Analyst",
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Registered new analyst: {new_user.email} (ID: {new_user.id})")

    token = create_access_token(new_user.id, new_user.email, new_user.role)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfileResponse(**new_user.to_dict()),
        message="Analyst registered and authenticated successfully.",
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate an analyst and issue a signed session bearer token."""
    normalized_email = str(request.email).lower().strip()

    user = db.query(User).filter(User.email == normalized_email).first()
    if not user:
        logger.warning(f"Failed login attempt: non-existent email '{normalized_email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid analyst email or security password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(request.password, user.password_hash):
        logger.warning(f"Failed login attempt: incorrect password for '{normalized_email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid analyst email or security password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This security analyst account has been deactivated.",
        )

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    logger.info(f"Analyst authenticated: {user.email}")

    token = create_access_token(user.id, user.email, user.role)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfileResponse(**user.to_dict()),
        message="Authentication successful.",
    )


@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve profile and clearance level for the currently authenticated analyst."""
    return UserProfileResponse(**current_user.to_dict())
