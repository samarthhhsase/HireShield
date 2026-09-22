from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.risk import RiskLevel, RiskSignal, ScoreBreakdown


class AnalysisResponse(BaseModel):
    id: str = Field(..., description="Unique analysis record identifier")
    candidate_id: str = Field(..., description="Referenced candidate identifier")
    candidate_name: str = Field(..., description="Candidate name")
    risk_score: int = Field(..., ge=0, le=100, description="Overall computed risk score")
    risk_level: RiskLevel = Field(..., description="Classification tier")
    signals: List[RiskSignal] = Field(default_factory=list, description="All detected risk signals")
    explanation: str = Field(..., description="Deterministic explainability summary")
    breakdown: ScoreBreakdown = Field(..., description="Score contributions per risk category")
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of analysis completion")
