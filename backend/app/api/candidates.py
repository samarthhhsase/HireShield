from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateResponse
from app.db.repository import BaseCandidateRepository, get_candidate_repository

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(
    candidate_in: CandidateCreate,
    repo: BaseCandidateRepository = Depends(get_candidate_repository),
):
    """Register a new candidate profile."""
    existing = repo.get_by_email(candidate_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Candidate with email '{candidate_in.email}' already exists.",
        )
    return repo.create(candidate_in)


@router.get("", response_model=List[CandidateResponse])
def list_candidates(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=200, description="Page size limit"),
    repo: BaseCandidateRepository = Depends(get_candidate_repository),
):
    """Retrieve all candidates with pagination."""
    return repo.list_all(skip=skip, limit=limit)


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: str,
    repo: BaseCandidateRepository = Depends(get_candidate_repository),
):
    """Get candidate details by unique identifier."""
    candidate = repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID '{candidate_id}' not found.",
        )
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: str,
    candidate_in: CandidateUpdate,
    repo: BaseCandidateRepository = Depends(get_candidate_repository),
):
    """Update candidate fields."""
    updated = repo.update(candidate_id, candidate_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID '{candidate_id}' not found.",
        )
    return updated


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(
    candidate_id: str,
    repo: BaseCandidateRepository = Depends(get_candidate_repository),
):
    """Delete a candidate record."""
    deleted = repo.delete(candidate_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID '{candidate_id}' not found.",
        )
    return None
