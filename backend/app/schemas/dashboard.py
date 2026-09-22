from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel, Field
from app.schemas.risk import RiskLevel


class DashboardSummary(BaseModel):
    total_candidates: int = Field(0, description="Total candidates in repository")
    analyses_completed: int = Field(0, description="Total risk analyses conducted")
    high_risk_candidates: int = Field(0, description="Candidates classified as HIGH or CRITICAL risk")
    average_risk_score: float = Field(0.0, description="Average risk score across all analyses")


class RiskDistribution(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class RecentAnalysisItem(BaseModel):
    analysis_id: str
    candidate_id: str
    candidate_name: str
    role: str
    risk_score: int
    risk_level: RiskLevel
    signal_count: int
    analyzed_at: datetime
