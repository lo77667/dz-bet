from __future__ import annotations
import json, time
from pathlib import Path
import pandas as pd
import requests
ROOT=Path(__file__).resolve().parents[1]
sample=pd.read_csv(ROOT/'data/interim/manual_validation_sample_2024_25.csv')
# Load OpenFootball with normalized lookup for the selected dates.
ALIASES={'Blackburn':'Blackburn Rovers','Derby':'Derby County','Norwich':'Norwich City','Watford':'Watford','Oxford':'Oxford United','Luton':'Luton Town','Hull':'Hull City','Swansea':'Swansea City','Sunderland':'Sunderland','Portsmouth':'Portsmouth','Bristol City':'Bristol City','Middlesbrough':'Middlesbrough','Plymouth':'Plymouth Argyle','West Brom':'West Bromwich Albion'}
def norm(x):
    value=str(x).strip()
    value=ALIASES.get(value,value)
    value=value.replace('AFC','').replace('FC','')
    return ''.join(ch.lower() for ch in value if ch.isalnum())
def score_text(home,away): return f'{int(home)}-{int(away)}'
of_by_date={}
of=json.loads((ROOT/'data/raw/openfootball/2024-25-championship.json').read_text())
for m in of['matches']:
    of_by_date.setdefault(m['date'],[]).append(m)
rows=[]
for _, r in sample.iterrows():
    date=pd.to_datetime(r['Date'],dayfirst=True).strftime('%Y%m%d')
    url=f'https://site.api.espn.com/apis/site/v2/sports/soccer/eng.2/scoreboard?dates={date}'
    resp=requests.get(url,timeout=30,headers={'User-Agent':'dz-bet-phase03d/1.0'})
    resp.raise_for_status(); payload=resp.json()
    espn_match=None
    for event in payload.get('events',[]):
        comp=event.get('competitions',[{}])[0]
        competitors=comp.get('competitors',[])
        names=[norm(c.get('team',{}).get('displayName','')) for c in competitors]
        if norm(r['HomeTeam']) in names or norm(r['AwayTeam']) in names:
            # Require both sides to reduce date-only false matches.
            if any(norm(r['HomeTeam'])==n for n in names) and any(norm(r['AwayTeam'])==n for n in names): espn_match=event; break
    of_match=None
    for m in of_by_date.get(pd.to_datetime(r['Date'],dayfirst=True).strftime('%Y-%m-%d'),[]):
        if {norm(r['HomeTeam']),norm(r['AwayTeam'])}.issubset({norm(m['team1']),norm(m['team2'])}): of_match=m; break
    espn_result='unknown'; espn_date='unknown'; espn_url=f'https://www.espn.com/soccer/scoreboard/_/league/eng.2/date/{date}'
    if espn_match:
        comp=espn_match['competitions'][0]; by_name={norm(c['team']['displayName']):c for c in comp['competitors']}
        home=next((c for n,c in by_name.items() if norm(r['HomeTeam'])==n),None); away=next((c for n,c in by_name.items() if norm(r['AwayTeam'])==n),None)
        if home and away: espn_result=score_text(home.get('score',0),away.get('score',0))
        espn_date=espn_match.get('date','')
    of_result='unknown'
    if of_match:
        ft=of_match['score'].get('ft') if isinstance(of_match['score'],dict) else of_match['score']; of_result=score_text(ft[0],ft[1])
    fd_result=score_text(r['FTHG'],r['FTAG'])
    rows.append({'sample_id':int(r['sample_id']),'date':r['Date'],'match':f"{r['HomeTeam']} vs {r['AwayTeam']}",'football_data_result':fd_result,'openfootball_result':of_result,'espn_result':espn_result,'espn_event_date':espn_date,'espn_url':espn_url,'agreement':'AGREE' if fd_result==espn_result else 'CHECK'})
    time.sleep(.2)
out=pd.DataFrame(rows); out.to_csv(ROOT/'data/interim/manual_validation_results_2024_25.csv',index=False)
print(out.to_string(index=False)); print('\nagreements=',(out.agreement=='AGREE').sum(),'of',len(out))
