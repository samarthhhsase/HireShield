from typing import List
from fastapi import APIRouter, Depends
from app.schemas.dashboard import DashboardSummary, RiskDistribution, RecentAnalysisItem
from app.schemas.risk import RiskLevel
from app.db.repository import (
    BaseCandidateRepository,
    BaseAnalysisRepository,
    get_candidate_repository,
    get_analysis_repository,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    candidate_repo: BaseCandidateRepository = Depends(get_candidate_repository),
    analysis_repo: BaseAnalysisRepository = Depends(get_analysis_repository),
):
    """
    Compute high-level recruitment risk metrics:
    - total candidates
    - analyses completed
    - high-risk candidates
    - average risk score
    """
    total_candidates = candidate_repo.count()
    analyses = analysis_repo.list_all(skip=0, limit=1000)
    analyses_completed = len(analyses)

    high_risk_candidates = sum(
        1 for a in analyses if a.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    )
    
    avg_score = 0.0
    if analyses_completed > 0:
        avg_score = round(sum(a.risk_score for a in analyses) / analyses_completed, 1)

    return DashboardSummary(
        total_candidates=total_candidates,
        analyses_completed=analyses_completed,
        high_risk_candidates=high_risk_candidates,
        average_risk_score=avg_score,
    )


@router.get("/risk-distribution", response_model=RiskDistribution)
def get_risk_distribution(
    analysis_repo: BaseAnalysisRepository = Depends(get_analysis_repository),
):
    """Return distribution breakdown across risk tiers."""
    analyses = analysis_repo.list_all(skip=0, limit=1000)
    
    distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    for a in analyses:
        if a.risk_level == RiskLevel.CRITICAL:
            distribution["critical"] += 1
        elif a.risk_level == RiskLevel.HIGH:
            distribution["high"] += 1
        elif a.risk_level == RiskLevel.MEDIUM:
            distribution["medium"] += 1
        else:
            distribution["low"] += 1

    return RiskDistribution(**distribution)


@router.get("/recent", response_model=List[RecentAnalysisItem])
def get_recent_analyses(
    candidate_repo: BaseCandidateRepository = Depends(get_candidate_repository),
    analysis_repo: BaseAnalysisRepository = Depends(get_analysis_repository),
):
    """Retrieve the most recent 5 completed candidate analyses."""
    analyses = analysis_repo.list_all(skip=0, limit=5)
    recent_items: List[RecentAnalysisItem] = []

    for a in analyses:
        candidate = candidate_repo.get_by_id(a.candidate_id)
        role = candidate.role if candidate else "General Profile"

        recent_items.append(
            RecentAnalysisItem(
                analysis_id=a.id,
                candidate_id=a.candidate_id,
                candidate_name=a.candidate_name,
                role=role,
                risk_score=a.risk_score,
                risk_level=a.risk_level,
                signal_count=len(a.signals),
                analyzed_at=a.analyzed_at,
            )
        )

    return recent_items
