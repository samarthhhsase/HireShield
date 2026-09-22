import httpx

url = 'https://www.naukri.com/job-listings-recruiter-sr-recruiter-mumbai-seagull-international-mumbai-0-to-5-years-180926012287?src=seo_srp&sid=17898977749152798&xp=1&px=1'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

with httpx.Client(follow_redirects=True, timeout=12.0, headers=headers) as client:
    res = client.get(url)
    with open('naukri_raw.html', 'w', encoding='utf-8') as f:
        f.write(res.text)
    print('Wrote naukri_raw.html, length:', len(res.text))
