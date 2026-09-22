import httpx
from bs4 import BeautifulSoup
import re

url = "https://www.naukri.com/job-listings-recruiter-sr-recruiter-mumbai-seagull-international-mumbai-0-to-5-years-180926012287?src=seo_srp&sid=17898977749152798&xp=1&px=1"

user_agents = {
    "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Bingbot": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Chrome Mobile": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
    "iPhone": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
}

for name, ua in user_agents.items():
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = httpx.get(url, headers=headers, follow_redirects=True, timeout=10.0)
        soup = BeautifulSoup(r.text, "html.parser")
        for s in soup(["script", "style", "noscript"]):
            s.decompose()
        text = soup.get_text(" ", strip=True)
        print(f"[{name}] Status: {r.status_code}, HTML len: {len(r.text)}, Extracted text len: {len(text)}")
        if len(text) > 0:
            print(f"  Preview: {text[:200]}")
    except Exception as e:
        print(f"[{name}] Error:", e)
