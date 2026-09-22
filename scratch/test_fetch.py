import httpx
from bs4 import BeautifulSoup
import json
import re

url = "https://www.naukri.com/job-listings-recruiter-sr-recruiter-mumbai-seagull-international-mumbai-0-to-5-years-180926012287?src=seo_srp&sid=17898977749152798&xp=1&px=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

try:
    with httpx.Client(follow_redirects=True, timeout=15.0, headers=headers) as client:
        r = client.get(url)
        print("Status:", r.status_code)
        print("Length:", len(r.text))
        soup = BeautifulSoup(r.text, "html.parser")
        print("Title:", soup.title.get_text() if soup.title else None)

        next_data = soup.find("script", id="__NEXT_DATA__")
        print("Has __NEXT_DATA__:", next_data is not None)
        if next_data and next_data.string:
            print("NEXT_DATA length:", len(next_data.string))
            data = json.loads(next_data.string)
            print("NEXT_DATA keys:", list(data.keys()))
            props = data.get("props", {})
            page_props = props.get("pageProps", {})
            print("pageProps keys:", list(page_props.keys()))

        json_ld = soup.find_all("script", type="application/ld+json")
        print("JSON-LD count:", len(json_ld))
        for i, jld in enumerate(json_ld):
            content = jld.string or ""
            print(f"JSON-LD [{i}] len: {len(content)} preview: {content[:150]}")

        # Let's see any other script tags containing job data
        for s in soup.find_all("script"):
            text = s.string or ""
            if "jobDescription" in text or "jobDetails" in text or "recruiter" in text.lower():
                print(f"Found candidate script tag (len {len(text)}) preview: {text[:200]}")
except Exception as e:
    print("Error:", e)
