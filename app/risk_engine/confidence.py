"""
Confidence Assessment Engine for HireShield.

Calculates evidence completeness independently from risk severity.
Answers: 'How much verifiable evidence do we have to substantiate this score?'
"""

from typing import Dict, Any, Optional, List


def calculate_confidence(
    job_text: Optional[str],
    domain_details: Dict[str, Any],
    recruiter_email: Optional[str],
    company_name: Optional[str],
    has_critical_indicators: bool = False
) -> float:
    """
    Computes confidence metric (0.0 to 1.0) based on signal coverage and data density.
    """
    confidence = 0.15  # Base starting value

    # 1. Text coverage
    if job_text:
        text_len = len(job_text.strip())
        if text_len >= 1000:
            confidence += 0.35
        elif text_len >= 400:
            confidence += 0.25
        elif text_len >= 100:
            confidence += 0.15
        else:
            confidence += 0.05

    # 2. Domain / Technical signals coverage
    if domain_details:
        dns_info = domain_details.get("dns", {})
        if dns_info.get("resolves") or dns_info.get("is_ip_hostname"):
            confidence += 0.15

        whois_info = domain_details.get("whois", {})
        if whois_info.get("whois_available"):
            confidence += 0.15

        ssl_info = domain_details.get("ssl", {})
        if ssl_info.get("ssl_valid") is not None:
            confidence += 0.10

    # 3. Recruiter contact vector
    if recruiter_email and "@" in recruiter_email:
        confidence += 0.10

    # 4. Employer entity vector
    if company_name and len(company_name.strip()) > 1:
        confidence += 0.05

    # 5. Definitive forensic evidence boost
    if has_critical_indicators:
        confidence += 0.15

    # Clamp and round to two decimal places
    final_confidence = max(0.10, min(0.98, confidence))
    return round(final_confidence, 2)
