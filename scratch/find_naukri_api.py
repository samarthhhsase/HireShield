import httpx
import re
import json

with open("scratch/rsc_dump.txt", encoding="utf-8") as f:
    text = f.read()

js_urls = re.findall(r'https://[^\"]+?\.js', text)
print("Found JS URLs:", len(js_urls))
for u in set(js_urls):
    print("JS:", u)

# Let's also check common Naukri job details API endpoints
job_id = "180926012287"
test_urls = [
    f"https://www.naukri.com/jobapi/v3/job/{job_id}",
    f"https://www.naukri.com/jobapi/v4/job/{job_id}",
    f"https://www.naukri.com/jobapi/v1/job/{job_id}",
    f"https://www.naukri.com/gateway/v1/job-details/{job_id}",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "appid": "109",
    "systemid": "Naukri",
    "clientid": "d3041050-4d4c-47ea-9a88-8422472d25d0",
}

for tu in test_urls:
    try:
        r = httpx.get(tu, headers=headers, timeout=10.0)
        print(f"URL: {tu} -> Status: {r.status_code}, Length: {len(r.text)}")
        if r.status_code == 200:
            print("Response preview:", r.text[:300])
    except Exception as e:
        print(f"URL: {tu} -> Error: {e}")
