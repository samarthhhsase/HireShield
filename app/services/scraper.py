import re
import logging
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("hireshield.scraper")

# Explicit Fetch Status Taxonomy
FETCH_SUCCESS = "FETCH_SUCCESS"
FETCH_BLOCKED = "FETCH_BLOCKED"
FETCH_NOT_FOUND = "FETCH_NOT_FOUND"
FETCH_RATE_LIMITED = "FETCH_RATE_LIMITED"
FETCH_SERVER_ERROR = "FETCH_SERVER_ERROR"
FETCH_TIMEOUT = "FETCH_TIMEOUT"
FETCH_NETWORK_ERROR = "FETCH_NETWORK_ERROR"
FETCH_INVALID_URL = "FETCH_INVALID_URL"
BROWSER_CONTENT_RECEIVED = "BROWSER_CONTENT_RECEIVED"
BROWSER_PROVIDED = BROWSER_CONTENT_RECEIVED

USER_AGENT = "HireShield-Security-Scanner/1.0 (+https://hireshield.ai/scanner-policy; recruitment-risk-auditor)"


def is_valid_url(url: str) -> bool:
    """Check if string is a valid HTTP/HTTPS URL with non-empty hostname."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def extract_job_page(url: str) -> dict:
    """
    Fetch and extract text content from a recruitment URL.
    Distinguishes server access restrictions (403/429) from content analysis.
    Never raises an uncaught exception for remote server status codes.
    """
    if not is_valid_url(url):
        logger.warning(f"Scanner received invalid URL format: {url}")
        return {
            "fetch_status": FETCH_INVALID_URL,
            "http_status": None,
            "message": "The provided target string is not a valid HTTP or HTTPS URL.",
            "fallback_available": False,
            "final_url": url,
            "redirect_count": 0,
            "title": "Invalid Target URL",
            "text": "",
        }

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        logger.info(f"Attempting page fetch: {url}")
        with httpx.Client(
            follow_redirects=True,
            timeout=12.0,
            headers=headers,
            verify=True,
        ) as client:
            response = client.get(url)

        final_url = str(response.url)
        redirect_count = len(response.history)
        status_code = response.status_code

        logger.info(f"Fetch completed for {url} with HTTP {status_code} ({redirect_count} redirects)")

        # 1. Successful response
        if status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
                tag.decompose()

            title = soup.title.get_text(" ", strip=True) if soup.title else ""
            text = soup.get_text(" ", strip=True)
            text = re.sub(r"\s+", " ", text)

            return {
                "fetch_status": FETCH_SUCCESS,
                "http_status": 200,
                "message": "Page successfully retrieved and parsed.",
                "fallback_available": False,
                "final_url": final_url,
                "redirect_count": redirect_count,
                "title": title[:300] or "Extracted Recruitment Posting",
                "text": text[:30000],
            }

        # 2. Access Blocked (HTTP 403) - e.g. Apple Careers WAF
        if status_code == 403:
            logger.info(f"Fetch blocked by target server (HTTP 403): {url}")
            return {
                "fetch_status": FETCH_BLOCKED,
                "http_status": 403,
                "message": "The target website blocked automated server-side access (HTTP 403 Forbidden).",
                "fallback_available": True,
                "final_url": final_url,
                "redirect_count": redirect_count,
                "title": "Access Restricted by Target Server",
                "text": "",
            }

        # 3. Not Found (HTTP 404)
        if status_code == 404:
            logger.info(f"Target URL not found (HTTP 404): {url}")
            return {
                "fetch_status": FETCH_NOT_FOUND,
                "http_status": 404,
                "message": "The target job posting was not found on the remote server (HTTP 404 Not Found).",
                "fallback_available": True,
                "final_url": final_url,
                "redirect_count": redirect_count,
                "title": "Posting Not Found",
                "text": "",
            }

        # 4. Rate Limited (HTTP 429)
        if status_code == 429:
            logger.info(f"Target server rate limited request (HTTP 429): {url}")
            return {
                "fetch_status": FETCH_RATE_LIMITED,
                "http_status": 429,
                "message": "The target server is rate limiting requests (HTTP 429 Too Many Requests).",
                "fallback_available": True,
                "final_url": final_url,
                "redirect_count": redirect_count,
                "title": "Rate Limit Exceeded",
                "text": "",
            }

        # 5. Remote Server Errors (500-599)
        if 500 <= status_code <= 599:
            logger.warning(f"Target server returned 5xx error (HTTP {status_code}): {url}")
            return {
                "fetch_status": FETCH_SERVER_ERROR,
                "http_status": status_code,
                "message": f"The target website server encountered an internal error (HTTP {status_code}).",
                "fallback_available": True,
                "final_url": final_url,
                "redirect_count": redirect_count,
                "title": f"Server Error (HTTP {status_code})",
                "text": "",
            }

        # 6. Other 4xx client errors (e.g. 401 Unauthorized)
        return {
            "fetch_status": FETCH_BLOCKED,
            "http_status": status_code,
            "message": f"The target website returned client error HTTP {status_code}.",
            "fallback_available": True,
            "final_url": final_url,
            "redirect_count": redirect_count,
            "title": f"Access Restricted (HTTP {status_code})",
            "text": "",
        }

    except httpx.TimeoutException:
        logger.warning(f"Fetch timed out for {url}")
        return {
            "fetch_status": FETCH_TIMEOUT,
            "http_status": None,
            "message": "Connection to the target website timed out after 12 seconds.",
            "fallback_available": True,
            "final_url": url,
            "redirect_count": 0,
            "title": "Connection Timeout",
            "text": "",
        }

    except (httpx.ConnectError, httpx.NetworkError, httpx.RequestError) as exc:
        logger.warning(f"Network error while fetching {url}: {exc}")
        return {
            "fetch_status": FETCH_NETWORK_ERROR,
            "http_status": None,
            "message": f"Network or DNS connection failed while reaching target website.",
            "fallback_available": True,
            "final_url": url,
            "redirect_count": 0,
            "title": "Network Connection Failure",
            "text": "",
        }

    except Exception as exc:
        logger.error(f"Unexpected exception while extracting page {url}: {exc}", exc_info=True)
        return {
            "fetch_status": FETCH_NETWORK_ERROR,
            "http_status": None,
            "message": f"Unexpected error while communicating with target server: {str(exc)}",
            "fallback_available": True,
            "final_url": url,
            "redirect_count": 0,
            "title": "Target Connection Error",
            "text": "",
        }
