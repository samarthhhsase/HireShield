"""
Lookalike and Brand Impersonation Detector for HireShield.

Computes pure-Python Levenshtein distance, normalized edit distance,
homoglyph substitution mapping, and compound brand keyword insertion.
"""

import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from app.risk_engine.risk_config import KNOWN_COMPANY_DOMAINS


# Common character homoglyphs / leetspeak substitutions used in typosquatting
HOMOGLYPH_MAP = {
    "0": "o",
    "1": "l",
    "3": "e",
    "4": "a",
    "5": "s",
    "8": "b",
    "@": "a",
}

# High-risk recruitment keywords appended to brand names
RECRUITMENT_AFFIXES = [
    "careers", "jobs", "hiring", "portal", "verify", "interview",
    "onboarding", "recruitment", "hr", "apply", "placement"
]


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes exact Levenshtein distance between two strings in pure Python."""
    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    v0 = list(range(len(s2) + 1))
    v1 = [0] * (len(s2) + 1)

    for i in range(len(s1)):
        v1[0] = i + 1
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        v0, v1 = v1, [0] * (len(s2) + 1)

    return v0[len(s2)]


def normalized_similarity(s1: str, s2: str) -> float:
    """Computes normalized similarity between 0.0 (completely distinct) and 1.0 (identical)."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1, s2)
    return round(1.0 - (dist / max_len), 4)


def dehomoglyph(text: str) -> str:
    """Replaces numeric/symbolic homoglyphs with their likely Latin letter equivalents."""
    res = text.lower()
    for char, rep in HOMOGLYPH_MAP.items():
        res = res.replace(char, rep)
    return res


def extract_sld(domain: str) -> str:
    """
    Extracts second-level domain name (e.g., 'microsoft' from 'microsoft.com'
    or 'micros0ft-careers' from 'micros0ft-careers.xyz').
    """
    parts = domain.split(".")
    if len(parts) >= 2:
        return parts[-2]
    return domain


def detect_lookalike_domain(
    domain: str,
    known_company_domains: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Analyzes a domain against known company brands to detect typosquatting,
    homoglyphs, and unauthorized brand keyword affixing.
    
    Returns:
    {
        "is_lookalike": bool,
        "matched_brand": str or None,
        "similarity": float,
        "risk_score": int,
        "evidence": str,
        "reason": str
    }
    """
    if known_company_domains is None:
        known_company_domains = KNOWN_COMPANY_DOMAINS

    clean_domain = domain.split(":")[0].strip().lower()
    if not clean_domain:
        return {
            "is_lookalike": False,
            "matched_brand": None,
            "similarity": 0.0,
            "risk_score": 0,
            "evidence": "",
            "reason": "Empty domain"
        }

    sld = extract_sld(clean_domain)
    normalized_sld = dehomoglyph(sld)

    highest_risk = 0
    matched_brand = None
    best_sim = 0.0
    best_evidence = ""
    best_reason = ""

    for brand_key, official_domain in known_company_domains.items():
        official_domain = official_domain.lower()
        official_sld = extract_sld(official_domain)

        # 1. Exact match or legitimate subdomain of the official domain -> NOT a lookalike!
        if clean_domain == official_domain or clean_domain.endswith("." + official_domain):
            continue

        # 2. Check compound keyword insertion (e.g. "microsoft-careers", "tcs-jobs", "amazon-hiring")
        for affix in RECRUITMENT_AFFIXES:
            compound_forms = [
                f"{brand_key}-{affix}",
                f"{brand_key}{affix}",
                f"{affix}-{brand_key}",
                f"{affix}{brand_key}"
            ]
            if any(cf in normalized_sld for cf in compound_forms):
                matched_brand = brand_key.title()
                highest_risk = max(highest_risk, 35)
                best_sim = max(best_sim, 0.90)
                best_evidence = f"Domain '{clean_domain}' embeds brand '{brand_key}' with recruitment affix '{affix}'"
                best_reason = "Unauthorized brand name combined with recruitment keyword"
                break

        # 3. Check Homoglyph / Leetspeak Typosquatting (e.g. micros0ft.com vs microsoft.com)
        if normalized_sld == official_sld and sld != official_sld:
            matched_brand = brand_key.title()
            highest_risk = max(highest_risk, 40)
            best_sim = max(best_sim, 0.95)
            best_evidence = f"Domain '{sld}' uses character substitution for '{official_sld}'"
            best_reason = "Typosquatting via homoglyph character replacement"
            break

        # 4. Check Normalized Edit Distance (Levenshtein)
        sim = normalized_similarity(sld, official_sld)
        # Edit distance of 1 or 2 on words of length >= 5 indicates typosquatting
        dist = levenshtein_distance(sld, official_sld)
        if 1 <= dist <= 2 and len(official_sld) >= 5 and sim >= 0.75:
            if sim > best_sim:
                best_sim = sim
                matched_brand = brand_key.title()
                highest_risk = max(highest_risk, 30)
                best_evidence = f"Domain '{sld}' has edit distance {dist} from '{official_sld}' ({round(sim * 100)}% similarity)"
                best_reason = "Close typographical similarity to established brand domain"

    is_lookalike = highest_risk > 0

    return {
        "is_lookalike": is_lookalike,
        "matched_brand": matched_brand,
        "similarity": best_sim,
        "risk_score": highest_risk,
        "evidence": best_evidence,
        "reason": best_reason
    }
