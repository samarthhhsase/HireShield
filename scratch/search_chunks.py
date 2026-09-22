import httpx
import re

urls = [
    "https://static.naukimg.com/s/9/121/_next/static/chunks/8139-6f0dda5e7556c6e0.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/main-app-41bfa04a3d4c7c6a.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/2443530c-e2a530f9c72a1395.js",
]

for u in urls:
    print("Fetching:", u)
    r = httpx.get(u)
    text = r.text
    for term in ["jobDetailsResp", "jobapi", "systemid", "clientid", "appid"]:
        matches = [m.start() for m in re.finditer(term, text)]
        print(f"  Term '{term}': {len(matches)} matches")
        for idx in matches[:2]:
            print("    ", text[max(0, idx-60):min(len(text), idx+100)])
