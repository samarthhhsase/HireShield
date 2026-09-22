import httpx
import re

url = "https://static.naukimg.com/s/9/121/_next/static/chunks/app/jd/page-fd985a2ef138267c.js"
r = httpx.get(url)
text = r.text
print("Size of page.js:", len(text))

# Let's search for URLs or endpoint patterns
for match in re.finditer(r'https?://[^\s"\'`]+|/jobapi/[^\s"\'`]+|/gateway/[^\s"\'`]+', text):
    print("Match:", match.group(0))

# Search for headers, appid, systemid, clientid
for kw in ["systemid", "appid", "clientid", "jobDetails", "fetchJob"]:
    m = [i.start() for i in re.finditer(kw, text, re.IGNORECASE)]
    print(f"Keyword {kw}: {len(m)} matches")
    for idx in m[:3]:
        print("  Snippet:", text[max(0, idx-60):min(len(text), idx+100)])
