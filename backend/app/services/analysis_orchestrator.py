import uuid
from datetime import datetime, timezone
from typing import Optional
from app.schemas.candidate import CandidateResponse
from app.schemas.analysis import AnalysisResponse
from app.services.nlp_service import get_nlp_service
from app.services.technical_analysis import get_technical_analysis_service
from app.services.risk_engine import calculate_risk


class AnalysisOrchestrator:
    """
    Coordinates the multi-stage hiring risk analysis pipeline:
    Candidate Data -> NLP Analysis -> Technical Analysis -> Signal Collection -> Risk Engine -> Explanation.
    """

    def __init__(self):
        self.nlp = get_nlp_service()
        self.technical = get_technical_analysis_service()

    def run_analysis(self, candidate: CandidateResponse) -> AnalysisResponse:
        # 1. NLP Analysis
        nlp_signals = self.nlp.analyze_text(
            resume_text=candidate.resume_text,
            job_description=candidate.job_description,
            declared_skills=candidate.skills,
        )

        # 2. Technical Analysis
        tech_signals = self.technical.analyze_technical(
            candidate_skills=candidate.skills,
            job_description=candidate.job_description,
            experience_years=candidate.experience_years,
            role=candidate.role,
        )

        # 3. Collect All Signals
        all_signals = nlp_signals + tech_signals

        # 4. Risk Engine Computation
        assessment = calculate_risk(all_signals)

        # 5. Build Final Response Model
        analysis_id = f"ANL-{uuid.uuid4().hex[:8].upper()}"
        return AnalysisResponse(
            id=analysis_id,
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level,
            signals=assessment.signals,
            explanation=assessment.explanation,
            breakdown=assessment.breakdown,
            analyzed_at=datetime.now(timezone.utc),
        )


analysis_orchestrator = AnalysisOrchestrator()


def get_analysis_orchestrator() -> AnalysisOrchestrator:
    return analysis_orchestrator
