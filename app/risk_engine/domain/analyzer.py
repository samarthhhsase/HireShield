"""
Unified Domain Intelligence Analyzer for HireShield.

Orchestrates WHOIS age, SSL validity, DNS resolution, and reputation checks.
Guarantees that a valid SSL certificate does not falsely clear a brand new or suspicious domain.
"""

from urllib.parse import urlparse
from typing import Dict, Any, List

from app.risk_engine.domain.whois import query_whois_info
from app.risk_engine.domain.ssl import check_ssl_certificate
from app.risk_engine.domain.dns import analyze_dns
from app.risk_engine.domain.reputation import analyze_reputation


def extract_domain_from_url(url_or_domain: str) -> str:
    """Extracts clean hostname from a URL or domain string."""
    if not url_or_domain:
        return ""
    val = url_or_domain.strip().lower()
    if not val.startswith("http://") and not val.startswith("https://"):
        val = "https://" + val
    try:
        parsed = urlparse(val)
        return parsed.netloc.split(":")[0].strip()
    except Exception:
        return url_or_domain.strip().lower()


def analyze_domain(url_or_domain: str) -> Dict[str, Any]:
    """
    Main entry point for Domain Intelligence.
    Returns domain risk score (0-100), red flag signals, positive trust signals,
    and granular inspection details.
    """
    domain = extract_domain_from_url(url_or_domain)
    if not domain:
        return {
            "domain_score": 0,
            "signals": [],
            "positive_signals": [],
            "details": {},
            "confidence": 0.1
        }

    signals: List[Dict[str, Any]] = []
    positive_signals: List[str] = []
    details: Dict[str, Any] = {}
    total_score = 0

    # 1. DNS Analysis
    dns_info = analyze_dns(domain)
    details["dns"] = dns_info

    if dns_info["is_private_network"]:
        signals.append({
            "category": "domain",
            "severity": "critical",
            "title": "Private or internal IP address detected",
            "description": "The destination URL resolves to a local/private network address (SSRF risk).",
            "score": 45
        })
        total_score += 45

    if dns_info["is_ip_hostname"]:
        signals.append({
            "category": "domain",
            "severity": "high",
            "title": "Direct IP address used as URL host",
            "description": "Legitimate employers do not host recruitment portals on raw IP addresses.",
            "score": 35
        })
        total_score += 35

    if dns_info["has_punycode"]:
        signals.append({
            "category": "domain",
            "severity": "high",
            "title": "Punycode or internationalized domain detected",
            "description": "Punycode (xn--) is frequently used for homoglyph domain spoofing.",
            "score": 30
        })
        total_score += 30

    if dns_info["is_excessive_subdomains"]:
        signals.append({
            "category": "domain",
            "severity": "medium",
            "title": "Excessive subdomain nesting",
            "description": f"Domain contains {dns_info['subdomain_count']} subdomain levels, often used to disguise actual hosts.",
            "score": 15
        })
        total_score += 15

    # 2. Reputation Analysis
    rep_info = analyze_reputation(url_or_domain)
    details["reputation"] = rep_info
    for s in rep_info["signals"]:
        signals.append({
            "category": "domain",
            "severity": s.get("severity", "medium"),
            "title": s.get("title", ""),
            "description": s.get("description", ""),
            "score": s.get("score", 0)
        })
        total_score += s.get("score", 0)

    for ps in rep_info["positive_signals"]:
        positive_signals.append(ps)

    # 3. WHOIS Analysis
    # Skip live external whois if raw IP or verified ATS to prevent latency
    whois_info = {}
    if not dns_info["is_ip_hostname"] and not rep_info["is_verified_ats"]:
        whois_info = query_whois_info(domain)
        details["whois"] = whois_info

        age_days = whois_info.get("age_days")
        if age_days is not None:
            if age_days < 30:
                signals.append({
                    "category": "domain",
                    "severity": "high",
                    "title": "Brand new domain registered < 30 days ago",
                    "description": f"The domain was registered only {age_days} days ago. Newly created domains have high scam correlation.",
                    "score": 35
                })
                total_score += 35
            elif age_days < 90:
                signals.append({
                    "category": "domain",
                    "severity": "medium",
                    "title": "Recently registered domain (< 90 days)",
                    "description": f"The domain is only {age_days} days old.",
                    "score": 20
                })
                total_score += 20
            elif age_days > 365:
                positive_signals.append(f"Domain is well-established (registered {age_days // 365} year(s) ago)")
    else:
        details["whois"] = {"skipped": True}

    # 4. SSL Analysis
    ssl_info = {}
    if not dns_info["is_ip_hostname"]:
        ssl_info = check_ssl_certificate(domain)
        details["ssl"] = ssl_info

        if ssl_info.get("ssl_valid"):
            positive_signals.append("HTTPS certificate is valid and active")
        else:
            signals.append({
                "category": "domain",
                "severity": "medium",
                "title": "Invalid or missing SSL certificate",
                "description": "The website lacks a valid TLS/SSL security certificate.",
                "score": 20
            })
            total_score += 20
    else:
        details["ssl"] = {"skipped": True}

    # 5. Normalization & ATS Mitigation
    if rep_info["is_verified_ats"]:
        # Verified platforms (e.g. greenhouse.io, lever.co, workday, linkedin) shouldn't be penalized
        domain_score = 0
    else:
        domain_score = max(0, min(100, total_score))

    # Confidence calculation based on how many checks succeeded
    data_points = 0
    if dns_info.get("resolves") or dns_info.get("is_ip_hostname"):
        data_points += 1
    if whois_info.get("whois_available"):
        data_points += 1
    if ssl_info.get("ssl_valid") is not None:
        data_points += 1

    confidence = round(0.50 + (data_points * 0.15), 2)
    confidence = min(0.95, confidence)

    return {
        "domain": domain,
        "domain_score": domain_score,
        "signals": signals,
        "positive_signals": positive_signals,
        "details": details,
        "confidence": confidence
    }
