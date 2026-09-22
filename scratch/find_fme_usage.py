import httpx
import re

chunks = [
    "https://static.naukimg.com/s/9/121/_next/static/chunks/2564-2180d4873bb221a8.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/8139-6f0dda5e7556c6e0.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/3354-222ae7dc5231d95f.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/2443530c-e2a530f9c72a1395.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/8339-2cd324859f354e7c.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/9363-7d249d727a04f538.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/7951-78c7b85f590425af.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/9822-87cb88f31873f817.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/1923-28a4c65d77951bd5.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/6394-c06eb145268e231f.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/app/jd/page-fd985a2ef138267c.js",
]

for url in chunks:
    try:
        r = httpx.get(url, timeout=10.0)
        t = r.text
        for prop in [".fmE", ".YNB"]:
            if prop in t:
                print(f"Found {prop} in {url.split('/')[-1]}")
                for m in re.finditer(re.escape(prop), t):
                    idx = m.start()
                    print("  Snippet:", t[max(0, idx-100):min(len(t), idx+200)])
    except Exception as e:
        print("Error:", e)
