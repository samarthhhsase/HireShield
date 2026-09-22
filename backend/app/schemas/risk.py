from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class RiskCategory(str, Enum):
    RESUME = "RESUME"
    NLP = "NLP"
    TECHNICAL = "TECHNICAL"
    VERIFICATION = "VERIFICATION"
    CONSISTENCY = "CONSISTENCY"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskSignal(BaseModel):
    signal_name: str = Field(..., description="Unique identifier or code for the risk signal")
    category: RiskCategory = Field(..., description="Classification category")
    severity: int = Field(..., ge=0, le=100, description="Severity score from 0 to 100")
    weight: float = Field(..., ge=0.0, le=1.0, description="Relative weighting contribution from 0.0 to 1.0")
    description: str = Field(..., description="Human-readable explanation of the detected risk signal")
    evidence: Optional[str] = Field(None, description="Direct supporting quote, data point, or observation")


class ScoreBreakdown(BaseModel):
    resume: int = 0
    nlp: int = 0
    technical: int = 0
    verification: int = 0
    consistency: int = 0


class RiskAssessment(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    signals: List[RiskSignal] = []
    explanation: str
    breakdown: ScoreBreakdown
