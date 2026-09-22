"""
Company Verification & Entity Consistency Module for HireShield.

Evaluates name-to-domain consistency, official company presence,
and corporate domain alignment without unfairly penalizing legitimate startups.
"""

import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from app.risk_engine.risk_config import KNOWN_COMPANY_DOMAINS, VERIFIED_ATS_PLATFORMS


def clean_company_name(name: str) -> str:
    """Normalizes company names by stripping corporate suffixes like Inc, LLC, Ltd, Pvt."""
    if not name:
        return ""
    normalized = name.lower().strip()
    normalized = re.sub(r"\b(inc|incorporated|llc|ltd|limited|corp|corporation|pvt|private|co)\b\.?", "", normalized)
    return normalized.strip()


def verify_company_entity(
    company_name: Optional[str],
    domain: Optional[str],
    recruiter_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates consistency between claimed company name, domain, and recruiter email.
    
    Returns company risk score (0-100), verified status, trust signals, and red flags.
    """
    signals: List[Dict[str, Any]] = []
    positive_signals: List[str] = []
    total_score = 0
    confidence = 0.50

    clean_name = clean_company_name(company_name or "")
    clean_domain = (domain or "").split(":")[0].strip().lower()

    if not clean_name and not clean_domain:
        return {
            "company_score": 15,  # Slight uncertainty
            "is_verified": False,
            "signals": [{
                "category": "company",
                "severity": "low",
                "title": "Unspecified employer details",
                "description": "Neither company name nor website was provided.",
                "score": 15
            }],
            "positive_signals": [],
            "confidence": 0.20
        }

    # 1. Check against Known Enterprise Brands
    is_known_brand = False
    official_brand_domain = None

    if clean_name:
        for brand, off_domain in KNOWN_COMPANY_DOMAINS.items():
            if brand in clean_name or clean_name in brand:
                is_known_brand = True
                official_brand_domain = off_domain
                break

    # 2. Check for Major Brand vs Suspicious Third-party Domain Mismatch
    if is_known_brand and official_brand_domain and clean_domain:
        is_official = clean_domain == official_brand_domain or clean_domain.endswith("." + official_brand_domain)
        is_ats = any(clean_domain == ats or clean_domain.endswith("." + ats) for ats in VERIFIED_ATS_PLATFORMS)

        if is_official or is_ats:
            positive_signals.append(f"Posting domain aligns with official {clean_name.title()} web presence")
            confidence = max(confidence, 0.90)
        else:
            # Claiming to be a Fortune 500 company on an unrelated domain
            score = 35
            total_score += score
            signals.append({
                "category": "company",
                "severity": "high",
                "title": f"Mismatched domain for claimed company ({clean_name.title()})",
                "description": f"The posting claims to be from {clean_name.title()}, but the domain '{clean_domain}' is not their official portal ({official_brand_domain}).",
                "score": score
            })
            confidence = max(confidence, 0.85)

    # 3. Check General Name-to-Domain Alignment for non-major brands
    elif clean_name and clean_domain:
        # Check if company name tokens appear inside domain SLD
        name_tokens = [t for t in re.split(r"[\s\-_]+", clean_name) if len(t) > 2]
        sld = clean_domain.split(".")[0] if "." in clean_domain else clean_domain

        token_match = any(token in sld for token in name_tokens) if name_tokens else False
        is_ats = any(clean_domain == ats or clean_domain.endswith("." + ats) for ats in VERIFIED_ATS_PLATFORMS)

        if token_match or is_ats:
            positive_signals.append(f"Domain '{clean_domain}' is consistent with company name '{clean_name.title()}'")
            confidence = max(confidence, 0.75)
        else:
            # Domain and company name have no visible lexical overlap
            # Note: This is an uncertainty factor (low severity), NOT an automatic scam accusation
            score = 15
            total_score += score
            signals.append({
                "category": "company",
                "severity": "low",
                "title": "Unverified company-to-domain consistency",
                "description": f"Company '{clean_name.title()}' has no obvious lexical relation to '{clean_domain}'. Could be an agency, third-party recruiter, or unverified entity.",
                "score": score
            })
            confidence = max(confidence, 0.60)

    # 4. Verified ATS presence
    if clean_domain and any(clean_domain == ats or clean_domain.endswith("." + ats) for ats in VERIFIED_ATS_PLATFORMS):
        positive_signals.append("Application hosted on recognized Applicant Tracking System (ATS)")
        total_score = max(0, total_score - 15)

    company_score = max(0, min(100, total_score))
    is_verified = len(positive_signals) > 0 and company_score == 0

    return {
        "company_score": company_score,
        "is_verified": is_verified,
        "signals": signals,
        "positive_signals": positive_signals,
        "confidence": round(confidence, 2)
    }
