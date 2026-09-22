import httpx
import re

r = httpx.get("https://static.naukimg.com/s/9/121/_next/static/chunks/9822-87cb88f31873f817.js")
text = r.text

mod_pos = text.find('75287:function')
mod_text = text[mod_pos:mod_pos+10000]

# Search for headers, appid, clientid, systemid in this module
print("Module 75287 snippet:")
for m in re.finditer(r'(?:headers|systemid|appid|clientid)[^\'"`]{0,100}', mod_text, re.I):
    print(" ", m.group(0))
