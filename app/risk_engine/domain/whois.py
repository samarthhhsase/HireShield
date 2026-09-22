"""
WHOIS and Domain Registration Intelligence for HireShield Domain Engine.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional

try:
    import whois
except ImportError:
    whois = None


def query_whois_info(domain: str) -> Dict[str, Any]:
    """
    Retrieves WHOIS registration data including creation date, expiry, registrar, and age in days.
    Provides graceful fallback when WHOIS is unavailable or blocked.
    """
    result = {
        "domain": domain,
        "creation_date": None,
        "expiry_date": None,
        "registrar": None,
        "age_days": None,
        "is_recent": False,
        "whois_available": False,
        "error": None
    }

    if not domain or whois is None:
        result["error"] = "whois library not installed or empty domain"
        return result

    # Strip port if present
    clean_domain = domain.split(":")[0].strip().lower()

    try:
        data = whois.whois(clean_domain)
        if not data:
            return result

        result["whois_available"] = True
        result["registrar"] = data.registrar if hasattr(data, "registrar") else None

        # Process creation date
        created = getattr(data, "creation_date", None)
        if isinstance(created, list):
            created = next((x for x in created if x), None)

        if isinstance(created, datetime):
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            result["creation_date"] = created.isoformat()
            age_days = max(0, (datetime.now(timezone.utc) - created).days)
            result["age_days"] = age_days
            # Flag domains registered less than 30 or 90 days ago
            result["is_recent"] = age_days < 90

        # Process expiry date
        expiry = getattr(data, "expiration_date", None)
        if isinstance(expiry, list):
            expiry = next((x for x in expiry if x), None)

        if isinstance(expiry, datetime):
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            result["expiry_date"] = expiry.isoformat()

    except Exception as e:
        result["error"] = str(e)

    return result
