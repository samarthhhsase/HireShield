import httpx

r = httpx.get("https://static.naukimg.com/s/9/121/_next/static/chunks/9822-87cb88f31873f817.js")
text = r.text

idx = text.find('WY:function(){return b}')
print("Found WY at", idx)
print(text[idx-50:idx+3000])
