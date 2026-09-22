"""
Careers Page & Portal Structure Checker for HireShield.
"""

from urllib.parse import urlparse
from typing import Dict, Any

from app.risk_engine.risk_config import VERIFIED_ATS_PLATFORMS


def evaluate_careers_structure(url: str) -> Dict[str, Any]:
    """
    Evaluates whether a URL structurally represents an authentic careers portal.
    """
    if not url:
        return {"is_careers_portal": False, "trust_level": "none", "notes": "No URL provided"}

    val = url.strip().lower()
    if not val.startswith("http://") and not val.startswith("https://"):
        val = "https://" + val

    parsed = urlparse(val)
    domain = parsed.netloc.split(":")[0].strip().lower()
    path = parsed.path.lower()

    # 1. Verified ATS platforms
    for ats in VERIFIED_ATS_PLATFORMS:
        if domain == ats or domain.endswith("." + ats):
            return {
                "is_careers_portal": True,
                "trust_level": "verified_ats",
                "notes": f"Official enterprise ATS platform ({ats})"
            }

    # 2. Corporate subdomain (e.g., careers.microsoft.com, jobs.apple.com)
    if domain.startswith("careers.") or domain.startswith("jobs."):
        return {
            "is_careers_portal": True,
            "trust_level": "corporate_subdomain",
            "notes": f"Official careers subdomain on '{domain}'"
        }

    # 3. Path structure (/careers, /jobs, /openings)
    if any(k in path for k in ["/careers", "/jobs", "/job-openings", "/positions", "/vacancies"]):
        return {
            "is_careers_portal": True,
            "trust_level": "path_structured",
            "notes": "Standard corporate /careers path found"
        }

    return {
        "is_careers_portal": False,
        "trust_level": "generic_page",
        "notes": "No standard careers portal markers found in URL structure"
    }
