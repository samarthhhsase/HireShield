import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.candidate import CandidateCreate, CandidateResponse
from app.services.candidate_service import (
    get_candidates,
    get_candidate_by_id,
    create_candidate,
    delete_candidate,
    get_activity_log,
    get_reports_list,
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
    db: Session = Depends(get_db),
):
    """
    Retrieve all analyzed candidate profiles and job threat dossiers from SQLite.
    Supports text search, threat level filtering, and pagination.
    """
    records = get_candidates(
        db,
        search=search,
        risk_level=risk_level,
        skip=skip,
        limit=limit,
    )
    return records


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
@router.get("/jobs/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a single candidate or job threat dossier by unique identifier (e.g. HS-2026-00421).
    """
    candidate = get_candidate_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate or job dossier with ID '{candidate_id}' not found.",
        )
    return candidate


@router.post("/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
@router.post("/jobs", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def add_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    """
    Manually persist a new candidate profile or evaluated job posting dossier into SQLite.
    """
    created = create_candidate(db, payload)
    return created


@router.delete("/candidates/{candidate_id}", status_code=status.HTTP_200_OK)
@router.delete("/jobs/{candidate_id}", status_code=status.HTTP_200_OK)
def remove_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """
    Delete a candidate or job dossier from the registry.
    """
    deleted = delete_candidate(db, candidate_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate or job dossier with ID '{candidate_id}' not found.",
        )
    return {"message": f"Dossier '{candidate_id}' deleted successfully.", "id": candidate_id}


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

