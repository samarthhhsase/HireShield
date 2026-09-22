from typing import List
from app.schemas.risk import (
    RiskAssessment,
    RiskCategory,
    RiskLevel,
    RiskSignal,
    ScoreBreakdown,
)

# Centralized threshold boundaries
RISK_THRESHOLDS = {
    RiskLevel.LOW: (0, 24),
    RiskLevel.MEDIUM: (25, 49),
    RiskLevel.HIGH: (50, 74),
    RiskLevel.CRITICAL: (75, 100),
}


def classify_risk_level(score: int) -> RiskLevel:
    """Deterministic tier classification based on score thresholds."""
    if score >= 75:
        return RiskLevel.CRITICAL
    elif score >= 50:
        return RiskLevel.HIGH
    elif score >= 25:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def calculate_risk(signals: List[RiskSignal]) -> RiskAssessment:
    """
    Transparent, deterministic risk calculation engine.
    
    Formula:
    Risk Score = Weighted average severity of all detected risk signals:
                 sum(signal.severity * signal.weight) / sum(signal.weight)
    
    Thresholds:
      0  – 24 : LOW
      25 – 49 : MEDIUM
      50 – 74 : HIGH
      75 – 100: CRITICAL
    """
    if not signals:
        return RiskAssessment(
            risk_score=0,
            risk_level=RiskLevel.LOW,
            signals=[],
            explanation="No adverse risk signals detected across resume, NLP, or technical evaluations.",
            breakdown=ScoreBreakdown(),
        )

    # Accumulate weighted contributions
    total_weighted_severity = 0.0
    total_weight = 0.0

    category_weighted = {
        RiskCategory.RESUME: 0.0,
        RiskCategory.NLP: 0.0,
        RiskCategory.TECHNICAL: 0.0,
        RiskCategory.VERIFICATION: 0.0,
        RiskCategory.CONSISTENCY: 0.0,
    }
    category_weights = {
        RiskCategory.RESUME: 0.0,
        RiskCategory.NLP: 0.0,
        RiskCategory.TECHNICAL: 0.0,
        RiskCategory.VERIFICATION: 0.0,
        RiskCategory.CONSISTENCY: 0.0,
    }

    for s in signals:
        weighted_val = s.severity * s.weight
        total_weighted_severity += weighted_val
        total_weight += s.weight

        category_weighted[s.category] += weighted_val
        category_weights[s.category] += s.weight

    if total_weight > 0:
        raw_score = total_weighted_severity / total_weight
    else:
        raw_score = 0.0

    final_score = int(min(100, max(0, round(raw_score))))
    risk_level = classify_risk_level(final_score)

    # Category breakdown (normalized to int for each category)
    def cat_score(cat: RiskCategory) -> int:
        w = category_weights[cat]
        if w > 0:
            return int(min(100, max(0, round(category_weighted[cat] / w))))
        return 0

    breakdown = ScoreBreakdown(
        resume=cat_score(RiskCategory.RESUME),
        nlp=cat_score(RiskCategory.NLP),
        technical=cat_score(RiskCategory.TECHNICAL),
        verification=cat_score(RiskCategory.VERIFICATION),
        consistency=cat_score(RiskCategory.CONSISTENCY),
    )

    # Explainability synthesis
    high_severity_signals = [s for s in signals if s.severity >= 50]
    if high_severity_signals:
        flag_names = ", ".join(s.signal_name for s in high_severity_signals[:3])
        explanation = (
            f"Risk score of {final_score}/100 ({risk_level.value}) generated from {len(signals)} detected signal(s). "
            f"Primary risk drivers: {flag_names}."
        )
    elif signals:
        explanation = (
            f"Risk score of {final_score}/100 ({risk_level.value}) derived from {len(signals)} minor observation(s). "
            f"No critical single-point failure vectors detected."
        )
    else:
        explanation = "Clean evaluation. All verified attributes meet target specifications."

    return RiskAssessment(
        risk_score=final_score,
        risk_level=risk_level,
        signals=signals,
        explanation=explanation,
        breakdown=breakdown,
    )
