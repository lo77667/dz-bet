from __future__ import annotations
import requests
url='https://www.football-data.co.uk/mmz4281/1920/E1.csv'
r=requests.get(url, allow_redirects=True, timeout=60, headers={'User-Agent':'Mozilla/5.0 dz-bet/0.3c'})
print('status=', r.status_code)
print('url=', r.url)
print('bytes=', len(r.content))
print('head=', r.text.splitlines()[0] if r.text else '')
