import httpx
from bs4 import BeautifulSoup

job_id = "180926012287"
candidates = [
    f"https://www.naukri.com/job-desc-ni/{job_id}",
    f"https://www.naukri.com/jd/{job_id}",
    f"https://www.naukri.com/job-listings-{job_id}",
    f"https://m.naukri.com/job-listings-{job_id}",
    f"https://m.naukri.com/job-desc/{job_id}",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

for u in candidates:
    try:
        r = httpx.get(u, headers=headers, follow_redirects=True, timeout=10.0)
        soup = BeautifulSoup(r.text, "html.parser")
        for s in soup(["script", "style"]):
            s.decompose()
        text = soup.get_text(" ", strip=True)
        print(f"URL: {u} -> Status: {r.status_code}, Final URL: {r.url}, Text len: {len(text)}")
        if len(text) > 100:
            print("  Preview:", text[:200])
    except Exception as e:
        print(f"URL: {u} -> Error: {e}")
