"""
HireShield NLP Engine Package.
"""

from app.risk_engine.nlp.analyzer import (
    analyze_job_text,
    extract_linguistic_features,
    detect_urgency,
    detect_payment_request,
    detect_credential_harvesting,
    detect_unrealistic_salary,
    detect_suspicious_contact_methods,
    detect_impersonation_language,
)

__all__ = [
    "analyze_job_text",
    "extract_linguistic_features",
    "detect_urgency",
    "detect_payment_request",
    "detect_credential_harvesting",
    "detect_unrealistic_salary",
    "detect_suspicious_contact_methods",
    "detect_impersonation_language",
]
