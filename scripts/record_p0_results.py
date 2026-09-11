from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
cache_dir=ROOT/"data/raw/footballcsv-cache/E1"; cache_dir.mkdir(parents=True,exist_ok=True)
sample=cache_dir/"2019-20-eng.2.csv"; shutil.copyfile('/tmp/fc_eng2_1920.csv',sample)
h=hashlib.sha256(sample.read_bytes()).hexdigest()
m= json.loads((ROOT/'data/MANIFEST.json').read_text())
m['sources']['footballcsv-cache']={'status':'downloaded_sample_no_odds','url':'https://raw.githubusercontent.com/footballcsv/cache.footballdata/master/2019-20/eng.2.csv','downloaded_at':datetime.now(timezone.utc).isoformat(),'sha256':h,'bytes':sample.stat().st_size,'encoding':'UTF-8','fields':['Date','Team 1','FT','HT','Team 2'],'odds_present':False}
m['source_metadata']['football-data-uk'].update({'status':'downloaded_via_requests','diagnostic':'data/raw/football-data-uk/E1/curl_L.log'})
m['source_metadata']['footballcsv-cache'].update({'status':'downloaded_sample_no_odds','downloaded_at':m['sources']['footballcsv-cache']['downloaded_at'],'sha256':h,'url':m['sources']['footballcsv-cache']['url']})
m['source_metadata']['openfootball'].update({'status':'downloaded_en2_championship','sha256':'per-season hashes in sources.openfootball'})
m['sources']['understat']={'status':'blocked','url':'https://understat.com','error':"soccerdata ValueError: Invalid league 'ENG-Championship'"}
for season, item in m['sources'].get('clubelo', {}).items():
    item.update({'status':'blocked_http_502','error':'curl HTTP/1.1 502 Bad Gateway','url':f'http://api.clubelo.com/{int(season[:4])+1}-06-30'})
m['notes'].append('P0: curl -L and requests succeeded for football-data; cache sample succeeded but is results-only; OpenFootball odds are absent.')
(ROOT/'data/MANIFEST.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
