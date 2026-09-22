"""
DNS and Network Intelligence for HireShield Domain Engine.
"""

import socket
import ipaddress
import re
from typing import Dict, Any, List


def is_ip_address(host: str) -> bool:
    """Checks if the hostname is a literal IPv4 or IPv6 address."""
    clean = host.split(":")[0].strip().strip("[]")
    try:
        ipaddress.ip_address(clean)
        return True
    except ValueError:
        return False


def is_private_ip(ip_str: str) -> bool:
    """Checks if an IP address belongs to private/loopback/link-local ranges (SSRF defense)."""
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_reserved
            or ip_obj.is_multicast
        )
    except ValueError:
        return False


def analyze_dns(domain: str) -> Dict[str, Any]:
    """
    Analyzes DNS resolution, IP address safety, punycode, and subdomain depth.
    """
    clean_host = domain.split(":")[0].strip().lower()

    result = {
        "domain": clean_host,
        "resolved_ips": [],
        "is_ip_hostname": False,
        "is_private_network": False,
        "has_punycode": False,
        "subdomain_count": 0,
        "is_excessive_subdomains": False,
        "resolves": False,
        "error": None
    }

    if not clean_host:
        result["error"] = "Empty domain"
        return result

    # 1. IP hostname check
    if is_ip_address(clean_host):
        result["is_ip_hostname"] = True
        result["resolved_ips"].append(clean_host)
        if is_private_ip(clean_host):
            result["is_private_network"] = True
        return result

    # 2. Punycode check (homoglyphs / IDN)
    if clean_host.startswith("xn--") or ".xn--" in clean_host:
        result["has_punycode"] = True

    # 3. Subdomain depth
    parts = clean_host.split(".")
    # e.g., "careers.tech.jobs.example.com" has 5 parts -> 3 subdomain levels
    subdomains = max(0, len(parts) - 2)
    result["subdomain_count"] = subdomains
    if subdomains >= 3:
        result["is_excessive_subdomains"] = True

    # 4. DNS resolution
    try:
        addr_info = socket.getaddrinfo(clean_host, None)
        ips = list({info[4][0] for info in addr_info if info and info[4]})
        result["resolved_ips"] = ips
        result["resolves"] = len(ips) > 0

        # Check for private IP binding (SSRF defense)
        for ip in ips:
            if is_private_ip(ip):
                result["is_private_network"] = True
                break
    except socket.gaierror as e:
        result["resolves"] = False
        result["error"] = f"DNS lookup failed: {str(e)}"
    except Exception as e:
        result["error"] = str(e)

    return result
