"""
Scoring and Weighted Aggregation Engine for HireShield.

Implements the normalized 7-component formula:
final_score = (
    NLP * 0.30 +
    DOMAIN * 0.20 +
    COMPANY * 0.15 +
    RECRUITER * 0.10 +
    PAYMENT_CREDENTIAL * 0.15 +
    SALARY * 0.05 +
    IMPERSONATION * 0.05
)

Also implements controlled, explainable critical signal overrides.
"""

from typing import Dict, Any, Tuple, Optional, List

from app.risk_engine.risk_config import WEIGHTS, RISK_THRESHOLDS


def determine_risk_level(score: float) -> str:
    """Maps numerical risk score (0-100) to human-readable risk tier."""
    clamped = max(0, min(100, round(score)))
    for level, (low, high) in RISK_THRESHOLDS.items():
        if low <= clamped <= high:
            return level
    return "CRITICAL" if clamped >= 75 else "LOW"


def evaluate_critical_overrides(
    nlp_features: List[Dict[str, Any]],
    domain_signals: List[Dict[str, Any]],
    impersonation_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Evaluates controlled high-severity overrides.
    Returns override metadata if a non-negotiable scam pattern is verified.
    """
    # 1. Upfront Payment / Fee demands
    for f in nlp_features:
        feat_name = f.get("feature", "")
        if any(term in feat_name for term in ["registration_fee", "security_deposit", "equipment_payment", "cash_to_apply"]):
            return {
                "override": True,
                "reason": f"Confirmed upfront payment request detected ({f.get('evidence', 'Registration fee')})",
                "severity": "critical",
                "min_score": 82
            }

    # 2. OTP / Password / PIN Credential Harvesting
    for f in nlp_features:
        feat_name = f.get("feature", "")
        if any(term in feat_name for term in ["otp_harvesting", "password_or_pin", "credit_card"]):
            return {
                "override": True,
                "reason": f"Direct credential or financial harvesting detected ({f.get('evidence', 'Sensitive credentials')})",
                "severity": "critical",
                "min_score": 88
            }

    # 3. Government ID / Bank Account Harvesting
    for f in nlp_features:
        feat_name = f.get("feature", "")
        if any(term in feat_name for term in ["upfront_government_id", "mandatory_id_registration", "premature_banking"]):
            return {
                "override": True,
                "reason": f"Premature government identity or banking details collection detected ({f.get('evidence', 'Identity documents')})",
                "severity": "critical",
                "min_score": 76
            }

    # 3. High-Confidence Brand Impersonation / Typosquatting
    if impersonation_data.get("is_lookalike") and impersonation_data.get("similarity", 0) >= 0.88:
        return {
            "override": True,
            "reason": f"Confirmed lookalike domain impersonating {impersonation_data.get('matched_brand')} ({impersonation_data.get('evidence')})",
            "severity": "critical",
            "min_score": 80
        }

    # 4. Critical Private Host / SSRF Attempt
    for s in domain_signals:
        if s.get("severity") == "critical" and "private or internal ip" in s.get("title", "").lower():
            return {
                "override": True,
                "reason": "Target host resolves to a private internal network IP (SSRF security hazard)",
                "severity": "critical",
                "min_score": 85
            }

    return None


def calculate_risk_score(
    nlp_score: float,
    domain_score: float,
    company_score: float,
    recruiter_score: float,
    payment_credential_score: float,
    salary_score: float,
    impersonation_score: float,
    nlp_features: Optional[List[Dict[str, Any]]] = None,
    domain_signals: Optional[List[Dict[str, Any]]] = None,
    impersonation_data: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None
) -> Tuple[int, str, Optional[Dict[str, Any]]]:
    """
    Computes normalized weighted final risk score (0-100), risk tier, and override status.
    """
    if weights is None:
        weights = WEIGHTS

    # Normalize each component to 0-100 bounds
    norm_nlp = max(0.0, min(100.0, float(nlp_score)))
    norm_domain = max(0.0, min(100.0, float(domain_score)))
    norm_company = max(0.0, min(100.0, float(company_score)))
    norm_recruiter = max(0.0, min(100.0, float(recruiter_score)))
    norm_pay_cred = max(0.0, min(100.0, float(payment_credential_score)))
    norm_salary = max(0.0, min(100.0, float(salary_score)))
    norm_impersonation = max(0.0, min(100.0, float(impersonation_score)))

    # Weighted calculation
    weighted_sum = (
        (norm_nlp * weights["nlp"]) +
        (norm_domain * weights["domain"]) +
        (norm_company * weights["company"]) +
        (norm_recruiter * weights["recruiter"]) +
        (norm_pay_cred * weights["payment_credential"]) +
        (norm_salary * weights["salary"]) +
        (norm_impersonation * weights["impersonation"])
    )

    raw_score = max(0, min(100, round(weighted_sum)))

    # Multi-category correlation boost (multiple independent weak signals elevate to MODERATE)
    active_categories = sum(
        1 for score_val in [norm_nlp, norm_domain, norm_company, norm_recruiter, norm_pay_cred, norm_salary, norm_impersonation]
        if score_val >= 10
    )
    if active_categories >= 3 and raw_score < 25:
        raw_score = 25

    # Check for controlled critical override
    override_info = evaluate_critical_overrides(
        nlp_features or [],
        domain_signals or [],
        impersonation_data or {}
    )

    final_score = raw_score
    if override_info and override_info.get("override"):
        min_required = override_info.get("min_score", 78)
        # When multiple critical vectors are detected (e.g. fee demand + ID harvesting), elevate to highest tier
        critical_count = sum(1 for f in (nlp_features or []) if f.get("severity") == "critical")
        if critical_count >= 2:
            min_required = max(min_required, 88)
        if final_score < min_required:
            final_score = min_required

    risk_level = determine_risk_level(final_score)

    return final_score, risk_level, override_info
