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

with httpx.Client(follow_redirects=True, timeout=15.0, headers=headers) as client:
    r = client.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    chunks = []
    for s in soup.find_all("script"):
        t = s.string or ""
        # Match self.__next_f.push([1,"..."])
        matches = re.findall(r'self\.__next_f\.push\(\[\d+,"(.*)"\]\)', t)
        for m in matches:
            chunks.append(m)
        if not matches and "self.__next_f" in t:
            chunks.append(t)

    full_rsc = "\n".join(chunks)
    print("Full RSC length:", len(full_rsc))
    # Look for mentions of job info, recruiter, description, etc.
    with open("scratch/rsc_dump.txt", "w", encoding="utf-8") as f:
        f.write(full_rsc)

    # Let's also check if there are API endpoints or embedded job detail JSON
    print("Contains 'jobDescription':", "jobDescription" in full_rsc)
    print("Contains 'companyName':", "companyName" in full_rsc)
    print("Contains 'title':", "title" in full_rsc)
    print("Contains 'Seagull':", "Seagull" in full_rsc)
    print("Contains 'Recruiter':", "Recruiter" in full_rsc)
    print("Contains 'jobId':", "jobId" in full_rsc)
