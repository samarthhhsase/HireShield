import httpx
r = httpx.get("https://static.naukimg.com/s/9/121/_next/static/chunks/9822-87cb88f31873f817.js")
text = r.text
pos = text.find('b="//www.naukri.com/jobapi/v4/job/"')
# Find enclosing function
func_start = text.rfind("function", 0, pos)
print("Function header:")
print(text[func_start:func_start+300])

# Find r.d(t, {...}) exports in this module
mod_start = text.rfind('{r.d(t,', 0, pos)
if mod_start == -1:
    mod_start = text.rfind('r.d(t,', 0, pos)
print("Module exports:")
print(text[mod_start:mod_start+400])
