import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.candidate import CandidateCreate, CandidateResponse
from app.services.auth_service import get_current_user, get_optional_current_user
from app.services.candidate_service import (
    get_candidates,
    get_candidate_by_id,
    create_candidate,
    delete_candidate,
    get_activity_log,
    get_reports_list,
    get_user_scans,
    get_user_scan_by_id,
)

logger = logging.getLogger("hireshield.api.candidates")

router = APIRouter(tags=["Candidate & Job Intelligence"])


@router.get("/candidates", response_model=List[CandidateResponse])
@router.get("/jobs", response_model=List[CandidateResponse])
def list_candidates(
    search: Optional[str] = Query(None, description="Search term matching title, company, candidate, or URL"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level: LOW, MEDIUM, HIGH, CRITICAL"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve analyzed candidate profiles and job threat dossiers from SQLite.
    When authenticated, isolates records to the authenticated analyst while retaining baseline demo data.
    """
    user_id = current_user.id if current_user else None
    records = get_candidates(
        db,
        search=search,
        risk_level=risk_level,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
    return records


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
@router.get("/jobs/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a single candidate or job threat dossier by unique identifier.
    Enforces authorization: demo data is open; user scans are private to their creator (HTTP 403 on IDOR).
    """
    user_id = current_user.id if current_user else None
    candidate = get_candidate_by_id(db, candidate_id, user_id=user_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate or job dossier with ID '{candidate_id}' not found.",
        )
    if candidate.get("_forbidden"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource.",
        )
    return candidate


@router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
@router.post("/jobs", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def add_candidate(
    payload: CandidateCreate,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Manually persist a new candidate profile or evaluated job posting dossier into SQLite.
    Associates the dossier with the authenticated user if logged in.
    """
    user_id = current_user.id if current_user else None
    created = create_candidate(db, payload, user_id=user_id)
    return created


@router.delete("/candidates/{candidate_id}", status_code=status.HTTP_200_OK)
@router.delete("/jobs/{candidate_id}", status_code=status.HTTP_200_OK)
def remove_candidate(
    candidate_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a candidate or job dossier from the registry with ownership verification.
    """
    user_id = current_user.id if current_user else None
    deleted = delete_candidate(db, candidate_id, user_id=user_id)
    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this resource.",
        )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate or job dossier with ID '{candidate_id}' not found.",
        )
    return {"message": f"Dossier '{candidate_id}' deleted successfully.", "id": candidate_id}


# =========================================================================
# User-Specific Scan History API (Strict Ownership & IDOR Protection)
# =========================================================================

@router.get("/scans")
def list_user_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve all scans conducted by the currently authenticated user.
    Backend strictly guarantees that User A only receives User A's scans.
    """
    scans = get_user_scans(db, user_id=current_user.id, skip=skip, limit=limit)
    return {
        "user_id": current_user.id,
        "total_scans": len(scans),
        "scans": scans,
    }


@router.get("/scans/{scan_id}")
def get_user_scan_detail(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific scan by ID, enforcing strict user ownership.
    Returns HTTP 403 Forbidden if the requested scan belongs to a different user.
    """
    result = get_user_scan_by_id(db, scan_id=scan_id, user_id=current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan record with ID '{scan_id}' not found.",
        )
    if result.get("_forbidden"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource.",
        )
    return result


@router.get("/reports")
def list_reports(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    """
    Retrieve security intelligence reports compiled from threat assessments and audit logs.
    """
    return get_reports_list(db, limit=limit)


@router.get("/activity")
def list_activity(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    """
    Retrieve live API telemetry, scan events, and audit logs.
    """
    return get_activity_log(db, limit=limit)
