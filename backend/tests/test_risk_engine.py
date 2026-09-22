from app.schemas.risk import RiskCategory, RiskLevel, RiskSignal
from app.services.risk_engine import calculate_risk, classify_risk_level


def test_empty_signals():
    """Empty signals should evaluate to 0 score and LOW risk."""
    assessment = calculate_risk([])
    assert assessment.risk_score == 0
    assert assessment.risk_level == RiskLevel.LOW
    assert len(assessment.signals) == 0
    assert "No adverse risk signals" in assessment.explanation


def test_low_risk():
    """Minor low-severity signal should produce LOW risk tier (0-24)."""
    signals = [
        RiskSignal(
            signal_name="MINOR_FORMATTING_NOTE",
            category=RiskCategory.RESUME,
            severity=15,
            weight=0.2,
            description="Minor typo or formatting anomaly in resume text.",
        )
    ]
    assessment = calculate_risk(signals)
    assert assessment.risk_level == RiskLevel.LOW
    assert 0 <= assessment.risk_score <= 24


def test_medium_risk():
    """Moderate signal should produce MEDIUM risk tier (25-49)."""
    signals = [
        RiskSignal(
            signal_name="UNCONFIRMED_COMMUNICATION_CHANNEL",
            category=RiskCategory.CONSISTENCY,
            severity=38,
            weight=0.3,
            description="Interview requests routed via informal messaging channels.",
        )
    ]
    assessment = calculate_risk(signals)
    assert assessment.risk_level == RiskLevel.MEDIUM
    assert 25 <= assessment.risk_score <= 49


def test_high_risk():
    """Substantial severity signal should produce HIGH risk tier (50-74)."""
    signals = [
        RiskSignal(
            signal_name="UNREALISTIC_GUARANTEE_LANGUAGE",
            category=RiskCategory.NLP,
            severity=60,
            weight=0.4,
            description="Guaranteed salary and immediate placement claims.",
        )
    ]
    assessment = calculate_risk(signals)
    assert assessment.risk_level == RiskLevel.HIGH
    assert 50 <= assessment.risk_score <= 74


def test_critical_risk():
    """Severe identity or fee demands should produce CRITICAL risk tier (75-100)."""
    signals = [
        RiskSignal(
            signal_name="FINANCIAL_OR_CREDENTIAL_SOLICITATION",
            category=RiskCategory.NLP,
            severity=88,
            weight=0.5,
            description="Direct demand for upfront processing deposit and Aadhaar credentials.",
        )
    ]
    assessment = calculate_risk(signals)
    assert assessment.risk_level == RiskLevel.CRITICAL
    assert 75 <= assessment.risk_score <= 100


def test_multiple_signals_accumulation():
    """Multiple compounding signals should scale risk score with explainable drivers."""
    signals = [
        RiskSignal(
            signal_name="FEE_REQUEST",
            category=RiskCategory.NLP,
            severity=75,
            weight=0.4,
            description="Mandatory verification fee required.",
        ),
        RiskSignal(
            signal_name="MISMATCH_SKILL",
            category=RiskCategory.TECHNICAL,
            severity=60,
            weight=0.3,
            description="Candidate does not possess core required skills.",
        ),
        RiskSignal(
            signal_name="URGENCY",
            category=RiskCategory.NLP,
            severity=50,
            weight=0.2,
            description="Urgent placement timeline.",
        ),
    ]
    assessment = calculate_risk(signals)
    assert assessment.risk_score == 64
    assert assessment.risk_level == RiskLevel.HIGH
    assert len(assessment.signals) == 3
    assert "FEE_REQUEST" in assessment.explanation
