import httpx

r = httpx.get("https://static.naukimg.com/s/9/121/_next/static/chunks/9822-87cb88f31873f817.js")
text = r.text

idx = text.find('25943:function')
print("Found 25943 at", idx)
print(text[idx:idx+2500])
