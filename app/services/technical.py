import socket
import ssl
import re
from datetime import datetime, timezone
from urllib.parse import urlparse
import ipaddress

try:
    import whois
except ImportError:
    whois = None


# High-abuse disposable TLDs frequently utilized for recruitment fraud campaigns
SCAM_TLDS = {
    ".xyz", ".top", ".online", ".site", ".buzz", ".work", ".click",
    ".monster", ".fit", ".rest", ".space", ".cfd", ".sbs", ".cam", ".vip",
}

# Recognized, verified applicant tracking systems & established enterprise job portals
VERIFIED_PLATFORMS = {
    "greenhouse.io",
    "lever.co",
    "myworkdayjobs.com",
    "ashbyhq.com",
    "smartrecruiters.com",
    "taleo.net",
    "icims.com",
    "bamboohr.com",
    "linkedin.com",
    "indeed.com",
    "naukri.com",
    "wellfound.com",
    "handshake.com",
    "glassdoor.com",
    "apple.com",
    "google.com",
    "microsoft.com",
    "amazon.jobs",
}

# Free website builders commonly abused to host fake corporate recruitment pages
FREE_HOSTING_DOMAINS = {
    "blogspot.com",
    "wixsite.com",
    "weebly.com",
    "wordpress.com",
    "sites.google.com",
    "carrd.co",
}

# Brand impersonation patterns in domain name (e.g. fake-google-jobs.com)
COMPOUND_BRAND_KEYWORDS = [
    r"google[-_]?(jobs|careers|hiring|portal)",
    r"amazon[-_]?(jobs|careers|hiring|verify)",
    r"apple[-_]?(jobs|careers|hiring)",
    r"microsoft[-_]?(jobs|careers|portal)",
    r"tcs[-_]?(jobs|careers|interview|onboarding)",
    r"infosys[-_]?(jobs|careers|interview)",
]


def _domain_age_days(domain: str):
    if whois is None:
        return None

    try:
        data = whois.whois(domain)
        created = data.creation_date

        if isinstance(created, list):
            created = next((x for x in created if x), None)

        if not created:
            return None

        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)

        return max(0, (datetime.now(timezone.utc) - created).days)
    except Exception:
        return None


def _ssl_valid(domain: str, port: int = 443):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=4) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as secure_sock:
                cert = secure_sock.getpeercert()

        not_after = cert.get("notAfter")
        if not_after:
            expiry = datetime.strptime(
                not_after, "%b %d %H:%M:%S %Y %Z"
            ).replace(tzinfo=timezone.utc)
            return expiry > datetime.now(timezone.utc)

        return True
    except Exception:
        return False


def _check_suspicious_patterns(url: str, domain: str) -> dict:
    """Analyze URL structure without fetching content (Layer A)."""
    is_ip = False
    try:
        ipaddress.ip_address(domain)
        is_ip = True
    except ValueError:
        is_ip = False

    subdomain_count = len(domain.split(".")) - 2 if not is_ip else 0
    has_at_symbol = "@" in url
    is_punycode = "xn--" in domain.lower()
    has_excessive_subdomains = subdomain_count >= 3

    # Check for scam TLDs
    has_scam_tld = any(domain.lower().endswith(tld) for tld in SCAM_TLDS)

    # Check for free hosting providers
    is_free_hosting = any(provider in domain.lower() for provider in FREE_HOSTING_DOMAINS)

    # Check for compound brand typosquatting
    has_brand_typosquatting = any(
        re.search(pattern, domain.lower()) for pattern in COMPOUND_BRAND_KEYWORDS
    )

    return {
        "is_ip_address": is_ip,
        "has_at_symbol": has_at_symbol,
        "is_punycode": is_punycode,
        "excessive_subdomains": has_excessive_subdomains,
        "has_scam_tld": has_scam_tld,
        "is_free_hosting": is_free_hosting,
        "has_brand_typosquatting": has_brand_typosquatting,
        "flagged": (
            is_ip
            or has_at_symbol
            or is_punycode
            or has_excessive_subdomains
            or has_scam_tld
            or is_free_hosting
            or has_brand_typosquatting
        ),
    }


def analyze_technical(url: str, redirect_count: int = 0) -> dict:
    """
    Layer A: Technical & URL Intelligence.
    Can be run independently even if the target page content was blocked.
    """
    parsed = urlparse(url)
    domain = (parsed.hostname or "").lower()

    dns_exists = False
    ip = None

    try:
        if domain:
            ip = socket.gethostbyname(domain)
            dns_exists = True
    except Exception:
        dns_exists = False

    is_https = parsed.scheme == "https"
    ssl_valid = is_https and _ssl_valid(domain)
    age_days = _domain_age_days(domain)
    patterns = _check_suspicious_patterns(url, domain)

    # Check if domain belongs to a verified enterprise platform or ATS
    is_verified_platform = any(
        domain == plat or domain.endswith(f".{plat}") for plat in VERIFIED_PLATFORMS
    )

    # Technical score is intentionally only 20% of the final risk.
    # An access limitation (like HTTP 403) does NOT add points.
    technical_score = 0

    if not dns_exists:
        technical_score += 50

    if not is_https:
        technical_score += 25

    if patterns["is_ip_address"]:
        technical_score += 30

    if patterns["has_at_symbol"]:
        technical_score += 35

    if patterns["is_punycode"]:
        technical_score += 20

    if patterns["excessive_subdomains"]:
        technical_score += 15

    if patterns.get("has_scam_tld"):
        technical_score += 25

    if patterns.get("is_free_hosting"):
        technical_score += 20

    if patterns.get("has_brand_typosquatting"):
        technical_score += 35

    if redirect_count >= 3:
        technical_score += 15
    elif redirect_count == 2:
        technical_score += 8

    if age_days is not None and age_days < 30:
        technical_score += 20
    elif age_days is not None and age_days < 180:
        technical_score += 10

    # Verified enterprise platform / ATS mitigates minor technical penalties
    if is_verified_platform:
        technical_score = min(technical_score, 10)

    technical_score = min(100, technical_score)

    checks = {
        "ssl_valid": ssl_valid,
        "domain_age_days": age_days,
        "dns_exists": dns_exists,
        "ip": ip,
        "redirect_count": redirect_count,
        "is_https": is_https,
        "is_verified_platform": is_verified_platform,
        "suspicious_patterns": patterns,
    }

    url_intelligence = {
        "domain": domain,
        "is_https": is_https,
        "dns_exists": dns_exists,
        "ssl_valid": ssl_valid,
        "domain_age_days": age_days,
        "ip": ip,
        "is_verified_platform": is_verified_platform,
        "suspicious_url_patterns": patterns["flagged"],
        "analysis_available": True,
    }

    return {
        "technical_score": technical_score,
        "checks": checks,
        "url_intelligence": url_intelligence,
    }
