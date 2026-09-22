"""
Recruiter & Contact Intelligence Analyzer for HireShield.

Analyzes recruiter email domains, disposable email services, free webmail vs corporate
domain alignment, and off-platform communication channels (WhatsApp / Telegram).
"""

import re
from typing import Dict, Any, List, Optional

from app.risk_engine.risk_config import (
    FREE_EMAIL_PROVIDERS,
    DISPOSABLE_EMAIL_DOMAINS,
    KNOWN_COMPANY_DOMAINS,
)


def extract_email_domain(email: str) -> Optional[str]:
    """Extracts lowercase domain component from an email address."""
    if not email or "@" not in email:
        return None
    return email.strip().split("@")[-1].lower()


def analyze_recruiter(
    recruiter_email: Optional[str] = None,
    company_name: Optional[str] = None,
    company_domain: Optional[str] = None,
    job_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates recruiter identity credibility and communication vectors.
    """
    signals: List[Dict[str, Any]] = []
    positive_signals: List[str] = []
    total_score = 0
    confidence = 0.50

    email_domain = extract_email_domain(recruiter_email or "")

    # 1. Recruiter Email Analysis
    if email_domain:
        confidence = 0.80

        # Check disposable temporary emails
        if email_domain in DISPOSABLE_EMAIL_DOMAINS or any(email_domain.endswith("." + d) for d in DISPOSABLE_EMAIL_DOMAINS):
            signals.append({
                "category": "recruiter",
                "severity": "critical",
                "title": "Disposable/burner email domain used by recruiter",
                "description": f"The contact email '{recruiter_email}' uses disposable email provider '{email_domain}'. Legitimate employers never use burner inboxes.",
                "score": 45
            })
            total_score += 45

        # Check public/free email providers (gmail, yahoo, etc.)
        elif email_domain in FREE_EMAIL_PROVIDERS:
            # Contextual evaluation: Is the claimed employer a major corporation?
            claimed_major_corp = False
            clean_company = (company_name or "").lower().strip()
            for brand in KNOWN_COMPANY_DOMAINS:
                if brand in clean_company:
                    claimed_major_corp = True
                    break

            if claimed_major_corp:
                # High severity: Major brand recruiting via personal @gmail.com
                signals.append({
                    "category": "recruiter",
                    "severity": "high",
                    "title": "Free webmail address claimed for major corporate recruiter",
                    "description": f"Recruiter uses free email '{email_domain}' while claiming to represent enterprise '{company_name}'. Major corporations recruit through corporate domains.",
                    "score": 35
                })
                total_score += 35
            else:
                # Weak signal: Freelance/small business recruiters often use Gmail
                signals.append({
                    "category": "recruiter",
                    "severity": "low",
                    "title": "Free email provider used by recruiter",
                    "description": f"Recruiter uses free webmail ({email_domain}) rather than a custom corporate domain. Typical for small businesses, but warrants verification.",
                    "score": 10
                })
                total_score += 10

        # Custom corporate email domain
        else:
            # Check domain match between email and company domain
            from app.risk_engine.risk_config import VERIFIED_ATS_PLATFORMS
            clean_company_domain = (company_domain or "").split(":")[0].strip().lower()
            is_ats = clean_company_domain in VERIFIED_ATS_PLATFORMS or any(clean_company_domain.endswith("." + ats) for ats in VERIFIED_ATS_PLATFORMS)

            if clean_company_domain and is_ats:
                clean_comp = (company_name or "").lower().strip()
                if clean_comp and (clean_comp in email_domain or email_domain.startswith(clean_comp)):
                    positive_signals.append(f"Recruiter email (@{email_domain}) aligns with employer '{company_name}' hosted on verified ATS ({clean_company_domain})")
                    confidence = 0.90
                else:
                    positive_signals.append(f"Recruiter uses custom corporate email domain (@{email_domain}) on ATS portal")
            elif clean_company_domain:
                if email_domain == clean_company_domain or email_domain.endswith("." + clean_company_domain):
                    positive_signals.append(f"Recruiter email domain (@{email_domain}) matches official company domain")
                    confidence = 0.90
                else:
                    signals.append({
                        "category": "recruiter",
                        "severity": "medium",
                        "title": "Mismatched recruiter email and company domain",
                        "description": f"Recruiter email domain (@{email_domain}) does not match the company domain ({clean_company_domain}).",
                        "score": 20
                    })
                    total_score += 20
            else:
                positive_signals.append(f"Recruiter uses custom corporate email domain (@{email_domain})")

    # 2. Communication Channel Analysis from Job Text
    if job_text:
        # Check for WhatsApp-only recruitment
        if re.search(r"\b(contact|apply|message|send\s+(?:cv|resume))\s*(?:only\s+)?(?:via|on)\s+whatsapp\b", job_text, re.I) or re.search(r"\bwhatsapp\s*(?:contact|only)?\s*:\s*[\+\d\s\-\(\)]{8,}", job_text, re.I):
            signals.append({
                "category": "recruiter",
                "severity": "medium",
                "title": "WhatsApp-only recruitment channel",
                "description": "Recruiter insists on communicating solely via personal messaging apps rather than official enterprise channels.",
                "score": 35
            })
            total_score += 35

        # Check for Telegram recruitment
        if re.search(r"\b(contact|dm|message)\s*(?:us|me|recruiter|team)?\s*(?:on|via)\s+telegram\b", job_text, re.I) or re.search(r"\btelegram\s*(?:username|id|channel|handle)?\s*:\s*@?\w+", job_text, re.I):
            signals.append({
                "category": "recruiter",
                "severity": "medium",
                "title": "Telegram recruitment channel",
                "description": "Recruiter conducts candidate screening via Telegram, a common vector for anonymous employment scams.",
                "score": 35
            })
            total_score += 35

    recruiter_score = max(0, min(100, total_score))

    return {
        "recruiter_score": recruiter_score,
        "signals": signals,
        "positive_signals": positive_signals,
        "confidence": round(confidence, 2)
    }
