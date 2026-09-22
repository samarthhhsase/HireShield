import httpx

url = "https://static.naukimg.com/s/9/121/_next/static/chunks/app/jd/page-fd985a2ef138267c.js"
r = httpx.get(url)
t = r.text

idx = t.find('url:"".concat(k.fmE)')
print(t[max(0, idx-500):min(len(t), idx+1000)])
