"""
HireShield Google Form & Recruitment Form Ingestion Service.

Fetches and extracts structured field data, questions, descriptions, and external links
from Google Forms and recruitment application portals with SSRF protection and graceful fallback.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

from app.risk_engine.domain.dns import is_private_ip, is_ip_address
from app.services.scraper import USER_AGENT, is_valid_url

logger = logging.getLogger("hireshield.services.form")


def is_google_form_url(url: str) -> bool:
    """Verifies whether the URL matches known Google Forms domains."""
    if not url or not isinstance(url, str):
        return False
    u = url.strip()
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    try:
        parsed = urlparse(u)
        hostname = (parsed.hostname or "").lower()
        if hostname == "forms.gle" or hostname.endswith(".forms.gle"):
            return True
        if (hostname == "google.com" or hostname.endswith(".google.com")) and "/forms" in (parsed.path or "").lower():
            return True
        return False
    except Exception:
        return False


def validate_form_url(url_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates form URL, checking scheme, length, and SSRF restrictions.
    Returns (is_valid, sanitized_url, error_message).
    """
    if not url_str or not str(url_str).strip():
        return False, None, "A valid recruitment form URL must be provided."

    cleaned = str(url_str).strip()
    if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
        cleaned = "https://" + cleaned

    if not is_valid_url(cleaned):
        return False, None, "Invalid URL structure. Please provide a valid HTTP or HTTPS form URL."

    parsed = urlparse(cleaned)
    hostname = parsed.hostname or ""

    if not hostname:
        return False, None, "URL must contain a valid domain name."

    # SSRF protection: reject localhost and private IP addresses
    if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False, None, "Access to localhost or loopback addresses is prohibited for security reasons."

    if is_ip_address(hostname) and is_private_ip(hostname):
        return False, None, "Access to private or internal network IP addresses is prohibited."

    return True, cleaned, None


def extract_form_content(url: str) -> Dict[str, Any]:
    """
    Fetches and extracts title, description, form questions/fields, and external links
    from a publicly accessible Google Form or recruitment form.
    """
    is_valid, sanitized_url, error_msg = validate_form_url(url)
    if not is_valid:
        return {
            "success": False,
            "status": "INVALID_URL",
            "message": error_msg or "Invalid form URL.",
            "fallback_available": False,
            "title": "",
            "description": "",
            "fields": [],
            "combined_text": "",
            "external_urls": [],
            "final_url": url,
        }

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        logger.info(f"Attempting Google Form fetch: {sanitized_url}")
        with httpx.Client(
            follow_redirects=True,
            timeout=12.0,
            headers=headers,
            verify=True,
        ) as client:
            response = client.get(sanitized_url)

        final_url = str(response.url)
        status_code = response.status_code

        # Detect Google Auth redirection / Private form / Login required
        final_host = urlparse(final_url).hostname or ""
        if "accounts.google.com" in final_host.lower():
            logger.info(f"Form requires Google authentication/login: {sanitized_url}")
            return {
                "success": False,
                "status": "FORM_ACCESS_RESTRICTED",
                "message": (
                    "Unable to access the form automatically because it requires Google account authentication or is private. "
                    "You can copy and paste the form questions and instructions into HireShield for instant threat analysis."
                ),
                "fallback_available": True,
                "title": "Private Google Form",
                "description": "",
                "fields": [],
                "combined_text": "",
                "external_urls": [],
                "final_url": final_url,
            }

        if status_code in (401, 403, 404):
            logger.info(f"Form returned HTTP {status_code}: {sanitized_url}")
            return {
                "success": False,
                "status": "FORM_ACCESS_RESTRICTED",
                "message": (
                    f"Target form returned HTTP {status_code} (access restricted, closed, or not found). "
                    "Paste the form questions or visible description into HireShield for manual risk analysis."
                ),
                "fallback_available": True,
                "title": "Access Restricted Form",
                "description": "",
                "fields": [],
                "combined_text": "",
                "external_urls": [],
                "final_url": final_url,
            }

        html_text = response.text
        # Detect "You need permission" or "Sign in to continue"
        if "You need permission" in html_text or "This form can only be viewed by users in the owner's organization" in html_text:
            return {
                "success": False,
                "status": "FORM_ACCESS_RESTRICTED",
                "message": (
                    "Unable to access the form automatically (restricted to organization domain). "
                    "Paste the form questions and job text into HireShield for analysis."
                ),
                "fallback_available": True,
                "title": "Organization-Restricted Form",
                "description": "",
                "fields": [],
                "combined_text": "",
                "external_urls": [],
                "final_url": final_url,
            }

        if "This form is no longer accepting responses" in html_text:
            return {
                "success": False,
                "status": "FORM_CLOSED",
                "message": (
                    "This Google Form is no longer accepting responses (closed by creator). "
                    "Paste any saved text or offer details into HireShield for analysis."
                ),
                "fallback_available": True,
                "title": "Closed Form",
                "description": "",
                "fields": [],
                "combined_text": "",
                "external_urls": [],
                "final_url": final_url,
            }

        soup = BeautifulSoup(html_text, "html.parser")

        # Extract title
        title = ""
        title_el = soup.find(class_=re.compile(r"freebirdFormviewerViewHeaderTitle|F9vfv|H2-header", re.I))
        if title_el:
            title = title_el.get_text(" ", strip=True)
        if not title and soup.title:
            title = soup.title.get_text(" ", strip=True)
            # Remove " - Google Forms" suffix if present
            title = re.sub(r"\s*-\s*Google Forms\s*$", "", title, flags=re.I)
        if not title:
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()
        title = title or "Recruitment Application Form"

        # Extract description
        description = ""
        desc_el = soup.find(class_=re.compile(r"freebirdFormviewerViewHeaderDescription|k32dtb", re.I))
        if desc_el:
            description = desc_el.get_text(" ", strip=True)
        if not description:
            og_desc = soup.find("meta", property="og:description")
            if og_desc and og_desc.get("content"):
                description = og_desc["content"].strip()

        # Extract form items/questions
        fields: List[str] = []
        # Google forms headings and question titles
        item_headers = soup.find_all(attrs={"role": "heading"})
        for h in item_headers:
            t = h.get_text(" ", strip=True)
            if t and t not in fields and t != title:
                fields.append(t)

        # Class-based fallback for questions
        q_elements = soup.find_all(class_=re.compile(r"freebirdFormviewerViewItemsItemItemTitle|M7eMe|HoPGnb", re.I))
        for q in q_elements:
            t = q.get_text(" ", strip=True)
            if t and t not in fields and t != title:
                fields.append(t)

        # Extract external links in form
        external_urls: List[str] = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("http://") or href.startswith("https://"):
                # Ignore internal google chrome/accounts/privacy links
                if not any(d in href for d in ["google.com/intl", "support.google.com", "policies.google.com", "accounts.google.com"]):
                    if href not in external_urls:
                        external_urls.append(href)

        # Also search raw text for links (e.g. wa.me / t.me)
        body_text = soup.get_text(" ", strip=True)
        raw_urls = re.findall(r"https?://[^\s<>\"'{}|\\^`\[\]]+", body_text, re.I)
        for u in raw_urls:
            if not any(d in u for d in ["google.com", "gstatic.com"]) and u not in external_urls:
                external_urls.append(u)

        # If nothing could be extracted
        if not description and not fields:
            # Fallback to general page text if possible
            general_text = re.sub(r"\s+", " ", body_text)
            if len(general_text) > 50:
                fields.append(general_text[:2000])

        if not description and not fields:
            return {
                "success": False,
                "status": "NO_EXTRACTABLE_CONTENT",
                "message": (
                    "Unable to extract visible questions or text from this form. "
                    "Please copy and paste the form questions and job text into HireShield directly."
                ),
                "fallback_available": True,
                "title": title,
                "description": "",
                "fields": [],
                "combined_text": "",
                "external_urls": external_urls,
                "final_url": final_url,
            }

        # Build clean structured text representation for risk engine
        text_lines = [f"Recruitment Form: {title}"]
        if description:
            text_lines.append(f"Description / Overview:\n{description}")
        if fields:
            text_lines.append("Requested Information & Application Fields:")
            for i, f in enumerate(fields, 1):
                text_lines.append(f"{i}. {f}")
        if external_urls:
            text_lines.append(f"External Links in Form: {', '.join(external_urls[:5])}")

        combined_text = "\n\n".join(text_lines)

        logger.info(f"Successfully extracted Google Form '{title}' with {len(fields)} fields and {len(external_urls)} external links.")

        return {
            "success": True,
            "status": "FETCH_SUCCESS",
            "message": f"Successfully extracted form with {len(fields)} question field(s).",
            "fallback_available": False,
            "title": title,
            "description": description,
            "fields": fields,
            "combined_text": combined_text,
            "external_urls": external_urls[:10],
            "final_url": final_url,
        }

    except httpx.TimeoutException:
        logger.warning(f"Timeout fetching Google Form: {sanitized_url}")
        return {
            "success": False,
            "status": "FETCH_TIMEOUT",
            "message": "Connection to the Google Form server timed out. Paste the form content into HireShield directly.",
            "fallback_available": True,
            "title": "Connection Timeout",
            "description": "",
            "fields": [],
            "combined_text": "",
            "external_urls": [],
            "final_url": sanitized_url,
        }
    except Exception as exc:
        logger.warning(f"Network error fetching Google Form: {exc}")
        return {
            "success": False,
            "status": "FETCH_ERROR",
            "message": f"Unable to reach the form: {str(exc)}. You can paste the form questions into HireShield for instant analysis.",
            "fallback_available": True,
            "title": "Network Error",
            "description": "",
            "fields": [],
            "combined_text": "",
            "external_urls": [],
            "final_url": sanitized_url,
        }
