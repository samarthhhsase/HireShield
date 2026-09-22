import httpx
import re

r = httpx.get("https://static.naukimg.com/s/9/121/_next/static/chunks/9822-87cb88f31873f817.js")
text = r.text

# Find where b is used
# Remember b is defined as: b="//www.naukri.com/jobapi/v4/job/"
# So it will be referenced as b or + b or (b,
matches = [m.start() for m in re.finditer(r'[\(,=]\s*b\s*\+', text)]
print(f"Matches for b +: {len(matches)}")
for idx in matches:
    print(text[max(0, idx-50):min(len(text), idx+200)])

matches_E = [m.start() for m in re.finditer(r'[\(,=]\s*E\s*\+', text)]
print(f"Matches for E +: {len(matches_E)}")
for idx in matches_E:
    print(text[max(0, idx-50):min(len(text), idx+200)])
