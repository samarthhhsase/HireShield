import httpx
import json

job_id = "180926012287"
url = f"https://www.naukri.com/jobapi/v4/job/{job_id}?microsite=y&brandedConsultantJd=true"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "clientid": "d3skt0p",
    "appid": "121",
    "systemid": "Naukri",
    "gid": "LOCATION,INDUSTRY,EDUCATION,FAREA_ROLE",
}

r = httpx.get(url, headers=headers, timeout=10.0)
print("Status:", r.status_code)
print("Length:", len(r.text))
if r.status_code == 200:
    data = r.json()
    print("Keys in response:", list(data.keys()))
    # Check jobDetails
    jd = data.get("jobDetails", {})
    print("Job title:", jd.get("title"))
    print("Company name:", jd.get("companyDetail", {}).get("name") or jd.get("companyName"))
    print("Job description snippet:", str(jd.get("description") or jd.get("jobDescription"))[:300])
    print("Experience:", jd.get("experienceStr"))
    print("Location:", jd.get("placeholders", [{}])[0].get("label") if jd.get("placeholders") else "N/A")
else:
    print("Error response:", r.text[:300])
