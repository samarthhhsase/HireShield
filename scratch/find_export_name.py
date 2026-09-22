import httpx
import re

r = httpx.get("https://static.naukimg.com/s/9/121/_next/static/chunks/9822-87cb88f31873f817.js")
text = r.text

pos = text.find('b="//www.naukri.com/jobapi/v4/job/"')
mod_start = text.rfind('r.d(t,', 0, pos)
mod_end = text.find('});', mod_start)
exports = text[mod_start:mod_end]

for m in re.finditer(r'([a-zA-Z0-9_\$]+):function\(\)\{return ([a-zA-Z0-9_]+)\}', exports):
    export_name, var_name = m.group(1), m.group(2)
    if var_name in ['b', 'E', 'w', 'O']:
        print(f"Export {export_name} -> {var_name}")
