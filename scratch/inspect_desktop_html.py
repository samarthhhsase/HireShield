import httpx
from bs4 import BeautifulSoup
import json

url = "https://www.naukri.com/job-listings-recruiter-sr-recruiter-mumbai-seagull-international-mumbai-0-to-5-years-180926012287?src=seo_srp&sid=17898977749152798&xp=1&px=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
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

with httpx.Client(follow_redirects=True, timeout=15.0, headers=headers) as client:
    r = client.get(url)
    print("Status:", r.status_code)
    soup = BeautifulSoup(r.text, "html.parser")
    
    print("\n--- META TAGS ---")
    for m in soup.find_all("meta"):
        print(m.attrs)
        
    print("\n--- LINK TAGS ---")
    for l in soup.find_all("link"):
        print(l.attrs)
        
    print("\n--- ALL TAGS IN BODY ---")
    tags = [t.name for t in soup.find_all()]
    print("Distinct tags:", set(tags))
