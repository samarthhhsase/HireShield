import httpx
r = httpx.get("https://static.naukimg.com/s/9/121/_next/static/chunks/9822-87cb88f31873f817.js")
pos = r.text.find('b="//www.naukri.com/jobapi/v4/job/"')
snippet = r.text[pos:pos+6000]
print("--- PART 2 ---")
print(snippet[1000:3000])
print("--- PART 3 ---")
print(snippet[3000:5500])
