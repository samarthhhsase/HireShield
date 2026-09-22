"""
Domain Reputation & URL Obfuscation Intelligence for HireShield.
"""

from urllib.parse import urlparse
from typing import Dict, Any, List

from app.risk_engine.risk_config import (
    SCAM_TLDS,
    FREE_HOSTING_DOMAINS,
    VERIFIED_ATS_PLATFORMS,
)


def analyze_reputation(url_or_domain: str) -> Dict[str, Any]:
    """
    Evaluates TLD abuse, free host exploitation, URL obfuscation,
    and verified ATS platform membership.
    """
    raw = url_or_domain.strip().lower()
    if not raw.startswith("http://") and not raw.startswith("https://"):
        raw_url = "https://" + raw
    else:
        raw_url = raw

    parsed = urlparse(raw_url)
    domain = parsed.netloc.split(":")[0].strip().lower()

    signals = []
    positive_signals = []
    score = 0

    # 1. Verified ATS whitelist check (Strong trust signal)
    is_verified_ats = False
    for ats in VERIFIED_ATS_PLATFORMS:
        if domain == ats or domain.endswith("." + ats):
            is_verified_ats = True
            positive_signals.append(f"Hosted on verified enterprise careers platform ({ats})")
            break

    # 2. Disposable / High-abuse Scam TLD check
    is_scam_tld = False
    for tld in SCAM_TLDS:
        if domain.endswith(tld):
            is_scam_tld = True
            signals.append({
                "signal": "high_abuse_tld",
                "severity": "high",
                "title": "High-risk top-level domain",
                "description": f"The domain uses high-abuse disposable TLD '{tld}' commonly used in scam campaigns.",
                "score": 35
            })
            score += 35
            break

    # 3. Free hosting check
    is_free_hosting = False
    for free_host in FREE_HOSTING_DOMAINS:
        if domain == free_host or domain.endswith("." + free_host):
            is_free_hosting = True
            signals.append({
                "signal": "free_hosting_service",
                "severity": "medium",
                "title": "Free web host or blog platform",
                "description": f"Recruitment page is hosted on a free website builder ({free_host}) instead of an official company domain.",
                "score": 25
            })
            score += 25
            break

    # 4. URL Obfuscation checks
    if "@" in parsed.netloc:
        signals.append({
            "signal": "url_userinfo_obfuscation",
            "severity": "high",
            "title": "URL contains credential obfuscation",
            "description": "The URL contains an '@' character, potentially spoofing the destination host.",
            "score": 40
        })
        score += 40

    if len(raw_url) > 200:
        signals.append({
            "signal": "excessive_url_length",
            "severity": "low",
            "title": "Abnormally long URL",
            "description": "The URL is unusually lengthy (>200 chars), which may be used to obscure the true domain.",
            "score": 10
        })
        score += 10

    return {
        "domain": domain,
        "is_verified_ats": is_verified_ats,
        "is_scam_tld": is_scam_tld,
        "is_free_hosting": is_free_hosting,
        "signals": signals,
        "positive_signals": positive_signals,
        "reputation_risk_score": min(100, score)
    }
