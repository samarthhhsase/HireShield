from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.analysis import AnalysisResponse
from app.db.repository import (
    BaseCandidateRepository,
    BaseAnalysisRepository,
    get_candidate_repository,
    get_analysis_repository,
)
from app.services.analysis_orchestrator import AnalysisOrchestrator, get_analysis_orchestrator

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/{candidate_id}", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
def analyze_candidate(
    candidate_id: str,
    candidate_repo: BaseCandidateRepository = Depends(get_candidate_repository),
    analysis_repo: BaseAnalysisRepository = Depends(get_analysis_repository),
    orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator),
):
    """
    Execute end-to-end risk intelligence analysis for a candidate:
    1. Verify candidate exists
    2. Gather candidate information
    3. Run NLP analysis
    4. Run technical analysis
    5. Collect signals
    6. Run Risk Engine
    7. Return structured analysis result
    """
    candidate = candidate_repo.get_by_id(candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot analyze candidate: ID '{candidate_id}' does not exist.",
        )

    # Run orchestrated risk analysis pipeline
    analysis_result = orchestrator.run_analysis(candidate)

    # Persist analysis result in analysis repository
    analysis_repo.save(analysis_result)

    return analysis_result


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis_by_id(
    analysis_id: str,
    analysis_repo: BaseAnalysisRepository = Depends(get_analysis_repository),
):
    """Retrieve an existing analysis record by ID."""
    analysis = analysis_repo.get_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{analysis_id}' not found.",
        )
    return analysis


@router.get("/candidate/{candidate_id}", response_model=List[AnalysisResponse])
def get_analyses_for_candidate(
    candidate_id: str,
    analysis_repo: BaseAnalysisRepository = Depends(get_analysis_repository),
):
    """Retrieve all historical analyses conducted for a specific candidate."""
    return analysis_repo.get_by_candidate_id(candidate_id)
