from typing import List, Dict, Any, Optional
from app.risk_engine.explanations import generate_verification_audit


def calculate_risk(
    behavioral: int = 0,
    linguistic: int = 0,
    structural: int = 0,
    technical: int = 0,
    red_flags: Optional[List[Dict[str, Any]]] = None,
    green_flags: Optional[List[Dict[str, Any]]] = None,
    content_analyzed: bool = True,
) -> Dict[str, Any]:
    """
    Calculate composite recruitment risk score, legitimacy score, and threat tier.

    IMPORTANT SEMANTIC DISTINCTION:
    '0 risk' is NOT the same as 'not analyzed'.
    When content_analyzed is False (e.g. target website returned HTTP 403 or blocked scraper),
    content-based recruitment risk cannot be determined.
    The system returns risk_score = None, risk_level = 'INCOMPLETE', and verdict = 'INCOMPLETE'.
    It does NOT invent a score of 0 or falsely classify the target as 'LOW'.
    """
    if not content_analyzed:
        return {
            "risk_score": None,
            "risk_level": "INCOMPLETE",
            "risk_assessment_status": "INCOMPLETE",
            "legitimacy_score": None,
            "fake_job_probability": None,
            "verdict": "INCOMPLETE",
            "red_flags": [],
            "green_flags": [],
            "recommendations": [
                "Submit visible job page content or use browser fallback to evaluate recruitment risk.",
            ],
            "content_analyzed": False,
            "risk_impact": 0,
            "explanation": "Insufficient page content for complete risk analysis. Layer B content analysis paused awaiting browser extraction.",
        }

    clean_red_flags = red_flags or []
    clean_green_flags = green_flags or []

    # 1. Base Layer A + Layer B calculation (35% B, 25% L, 20% S, 20% T)
    raw_score = (
        (behavioral or 0) * 0.35
        + (linguistic or 0) * 0.25
        + (structural or 0) * 0.20
        + (technical or 0) * 0.20
    )

    # 2. Green Flag Trust Mitigation:
    # If legitimate corporate indicators exist and no critical fraud threats were detected,
    # gently dampen minor score noise to protect legitimate corporate postings.
    has_critical_red_flags = any(
        f.get("severity") == "critical" for f in clean_red_flags
    )
    if clean_green_flags and not has_critical_red_flags:
        green_trust_bonus = sum(g.get("trust_bonus", 10) for g in clean_green_flags)
        dampening = min(15.0, green_trust_bonus * 0.25)
        raw_score = max(0.0, raw_score - dampening)

    score = round(min(100, max(0, raw_score)))

    # 3. Multi-Vector Fraud Overrides:
    messages = " ".join(flag.get("message", "").lower() for flag in clean_red_flags)
    has_sensitive = (
        "sensitive identity" in messages
        or "bank account details" in messages
        or "authentication credentials" in messages
    )
    has_banking_or_otp = (
        "authentication credentials" in messages
        or "bank account details" in messages
        or "password" in messages
        or "otp" in messages
    )
    has_payment = "payment" in messages or "fee" in messages
    has_check_cashing = "check cashing" in messages or "vendor reimbursement" in messages or "reshipping" in messages
    has_free_email_impersonation = "free, generic public email" in messages or "corporate brand claimed" in messages
    has_interview_bypass = "without formal interview" in messages or "offer letter" in messages
    has_lure = "lure archetype" in messages or "task lure" in messages
    has_guarantee = "unrealistic claim" in messages or "guarantees" in messages
    has_urgency = "urgency" in messages or "scarcity" in messages

    # Override 1: Simultaneous payment + sensitive identity requests (CRITICAL >= 85)
    if has_sensitive and has_payment:
        score = max(score, 85)

    # Override 2: Check cashing / equipment vendor scam / money mule (CRITICAL >= 80)
    elif has_check_cashing:
        score = max(score, 80)

    # Override 3: Upfront payment or mandatory fee requested (CRITICAL >= 75)
    elif has_payment:
        score = max(score, 75)

    # Override 4: Critical credential/banking solicitation or cumulative behavioral threat (CRITICAL >= 75)
    elif has_banking_or_otp or (behavioral and behavioral >= 70):
        score = max(score, 75)

    # Override 5: Corporate brand impersonation via free public email (HIGH >= 65)
    elif has_free_email_impersonation:
        score = max(score, 65)

    # Override 6: Direct interview bypass + informal messaging (HIGH >= 65)
    elif has_interview_bypass and ("informal messaging" in messages or "whatsapp" in messages or "telegram" in messages):
        score = max(score, 65)

    # Override 7: Work-from-home task/captcha lure with guarantees/urgency (HIGH >= 55)
    elif has_lure and (has_guarantee or has_urgency):
        score = max(score, 55)

    # 4. Determine Threat Tier
    if score >= 75:
        level = "CRITICAL"
        verdict = "CONFIRMED_SCAM"
        fake_prob = min(99, max(85, score))
    elif score >= 50:
        level = "HIGH"
        verdict = "HIGH_RISK_FAKE"
        fake_prob = min(84, max(55, score))
    elif score >= 25:
        level = "MEDIUM"
        verdict = "SUSPICIOUS"
        fake_prob = min(54, max(28, score))
    else:
        level = "LOW"
        fake_prob = max(1, min(18, score))
        if len(clean_green_flags) >= 2 or (technical or 0) <= 10:
            verdict = "VERIFIED_REAL"
        else:
            verdict = "LIKELY_REAL"

    # 5. Determine Legitimacy Score (0 to 100)
    if score >= 75:
        legitimacy_score = max(0, 100 - score - 10)
    elif score < 25:
        legitimacy_boost = min(15, len(clean_green_flags) * 5)
        legitimacy_score = min(100, max(80, 100 - score + legitimacy_boost))
    else:
        legitimacy_score = max(0, min(100, 100 - score))

    # 6. Actionable Candidate Safety Recommendations
    recommendations = []
    if has_payment:
        recommendations.append(
            "NEVER transfer money, registration fees, or equipment deposits. Legitimate employers never charge candidates."
        )
    if has_sensitive:
        recommendations.append(
            "Do not provide Aadhaar, PAN, SSN, or bank account details before receiving a verified written offer and formal onboarding."
        )
    if has_check_cashing:
        recommendations.append(
            "Refuse any requests to deposit checks, forward packages, or purchase supplies from designated 'vendors'."
        )
    if has_free_email_impersonation:
        recommendations.append(
            "Verify recruiter authenticity through the official company career website. Legitimate corporate HR does not hire from generic free email addresses."
        )
    if "informal messaging" in messages:
        recommendations.append(
            "Insist on communicating through verified corporate email domains or official applicant tracking systems rather than Telegram or WhatsApp."
        )
    if not recommendations:
        if clean_green_flags:
            recommendations.append(
                "Posting exhibits strong hallmarks of legitimate corporate recruitment (EEO disclosures, verified benefits, formal qualifications)."
            )
        else:
            recommendations.append(
                "Standard diligence recommended: verify listing on official company careers portal before submitting personal information."
            )

    # 7. Explainable Synthesis
    if score >= 75:
        explanation = (
            f"CRITICAL RECRUITMENT THREAT: Risk score of {score}/100 ({level}) with {fake_prob}% scam probability. "
            f"Primary threat drivers: {', '.join(f.get('message', '') for f in clean_red_flags[:3])}."
        )
    elif score >= 50:
        explanation = (
            f"HIGH RISK DETECTED: Risk score of {score}/100 ({level}) with {fake_prob}% scam probability. "
            f"Suspicious recruitment patterns identified. Exercise extreme caution."
        )
    elif score >= 25:
        explanation = (
            f"MODERATE ADVISORY: Risk score of {score}/100 ({level}). "
            f"Minor anomalies detected. Candidate verification recommended."
        )
    else:
        green_summary = f" Supported by {len(clean_green_flags)} verified legitimacy markers." if clean_green_flags else ""
        explanation = (
            f"Full multi-layer assessment complete. Risk score of {score}/100 ({level}) - {verdict}. "
            f"Legitimacy confidence: {legitimacy_score}%.{green_summary}"
        )

    pos_signals = [
        g.get("message", str(g)) if isinstance(g, dict) else str(g)
        for g in clean_green_flags
    ]
    analysis_dict = {
        "domain": {"score": technical or 0},
        "nlp": {"score": max(behavioral or 0, linguistic or 0)},
        "company": {"score": 35 if has_free_email_impersonation else 0},
        "recruiter": {"score": 35 if has_free_email_impersonation or "informal messaging" in messages else 0},
        "salary": {"score": 0},
        "impersonation": {"is_lookalike": False}
    }
    verification_audit = generate_verification_audit(
        risk_score=score,
        risk_level=level,
        signals=clean_red_flags,
        positive_signals=pos_signals,
        analysis=analysis_dict
    )

    return {
        "risk_score": score,
        "risk_level": level,
        "risk_assessment_status": "COMPLETE",
        "legitimacy_score": legitimacy_score,
        "fake_job_probability": fake_prob,
        "verdict": verdict,
        "red_flags": clean_red_flags,
        "green_flags": clean_green_flags,
        "recommendations": recommendations,
        "verification_audit": verification_audit,
        "content_analyzed": True,
        "risk_impact": None,
        "explanation": explanation,
    }
