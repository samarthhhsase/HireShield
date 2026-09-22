import httpx
import re

url = "https://static.naukimg.com/s/9/121/_next/static/chunks/app/jd/page-fd985a2ef138267c.js"
r = httpx.get(url)
text = r.text

m = [i.start() for i in re.finditer(r'saveJobDetailsAction', text)]
for idx in m:
    print("saveJobDetailsAction match:")
    print(text[max(0, idx-200):min(len(text), idx+400)])
