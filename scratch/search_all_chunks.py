import httpx
import re

chunks = [
    "https://static.naukimg.com/s/9/121/_next/static/chunks/2564-2180d4873bb221a8.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/8139-6f0dda5e7556c6e0.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/3354-222ae7dc5231d95f.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/webpack-1cadc98aefea2ec0.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/2443530c-e2a530f9c72a1395.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/8339-2cd324859f354e7c.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/9363-7d249d727a04f538.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/7951-78c7b85f590425af.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/9822-87cb88f31873f817.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/1923-28a4c65d77951bd5.js",
    "https://static.naukimg.com/s/9/121/_next/static/chunks/6394-c06eb145268e231f.js",
]

for url in chunks:
    try:
        r = httpx.get(url, timeout=10.0)
        t = r.text
        if "75287:" in t or "jobapi" in t or "job-details" in t:
            print("FOUND IN:", url)
            for m in re.finditer(r'(?:jobapi|job-details|75287)[^\'"`]{0,100}', t):
                print("  ", m.group(0))
    except Exception as e:
        print("Error on", url, e)
