"""
SSL / TLS Certificate Intelligence for HireShield Domain Engine.

IMPORTANT SECURITY RULE:
A valid SSL certificate alone MUST NOT make a website safe.
Free automated certificates (e.g. Let's Encrypt / cPanel) are widely used on malicious domains.
"""

import socket
import ssl
from datetime import datetime, timezone
from typing import Dict, Any


def check_ssl_certificate(domain: str, port: int = 443, timeout: float = 3.5) -> Dict[str, Any]:
    """
    Connects via TLS to inspect the host certificate validity, issuer, and expiration date.
    Returns certificate details and validity flags.
    """
    clean_domain = domain.split(":")[0].strip().lower()

    result = {
        "domain": clean_domain,
        "ssl_valid": False,
        "issuer": None,
        "expiry_date": None,
        "days_to_expiry": None,
        "error": None,
        "is_free_automated_ca": False
    }

    if not clean_domain:
        result["error"] = "Empty domain"
        return result

    try:
        context = ssl.create_default_context()
        with socket.create_connection((clean_domain, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=clean_domain) as secure_sock:
                cert = secure_sock.getpeercert()

        if not cert:
            result["error"] = "No certificate presented"
            return result

        # Check expiration date
        not_after = cert.get("notAfter")
        if not_after:
            expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            result["expiry_date"] = expiry.isoformat()
            now = datetime.now(timezone.utc)
            result["ssl_valid"] = expiry > now
            result["days_to_expiry"] = (expiry - now).days
        else:
            result["ssl_valid"] = True

        # Extract issuer details
        issuer_tuple = cert.get("issuer", ())
        issuer_dict = {}
        for rdn in issuer_tuple:
            for k, v in rdn:
                issuer_dict[k] = v

        issuer_org = issuer_dict.get("organizationName", issuer_dict.get("commonName", "Unknown"))
        result["issuer"] = issuer_org

        # Check if automated/free certificate (common on ephemeral phishing domains)
        if any(ca in str(issuer_org).lower() for ca in ["let's encrypt", "zerossl", "cpanel", "cloudflare"]):
            result["is_free_automated_ca"] = True

    except Exception as e:
        result["ssl_valid"] = False
        result["error"] = str(e)

    return result
