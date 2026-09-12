from __future__ import annotations
import json, re
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
SEASONS=['2019-20','2020-21','2021-22','2022-23','2023-24','2024-25','2025-26']
ALIASES={"QPR":"Queens Park Rangers","Sheff Utd":"Sheffield United","Sheff Wed":"Sheffield Wednesday","Sheffield Weds":"Sheffield Wednesday","Nott'm Forest":"Nottingham Forest","West Brom":"West Bromwich Albion","Blackburn":"Blackburn Rovers","Birmingham":"Birmingham City","Charlton":"Charlton Athletic","Coventry":"Coventry City","Huddersfield":"Huddersfield Town","Luton":"Luton Town","Norwich":"Norwich City","Stoke":"Stoke City","Swansea":"Swansea City","Wigan":"Wigan Athletic","Rotherham":"Rotherham United","Cardiff":"Cardiff City","Derby":"Derby County","Leeds":"Leeds United","Watford":"Watford","Millwall":"Millwall","Bristol City":"Bristol City","Preston":"Preston North End","Hull":"Hull City","Plymouth":"Plymouth Argyle","Ipswich":"Ipswich Town","Oxford":"Oxford United","Middlesbrough":"Middlesbrough","Bournemouth":"AFC Bournemouth","Leicester":"Leicester City","Peterboro":"Peterborough United","Wycombe":"Wycombe Wanderers"}
def team(x): return ALIASES.get(re.sub(r'\s+(FC|AFC)$','',str(x).strip()),re.sub(r'\s+(FC|AFC)$','',str(x).strip()))
rows=[]
for season in SEASONS:
 fd=pd.read_csv(ROOT/'data/raw/football-data-uk/E1'/f'{season}.csv',encoding='latin-1'); fd['date']=pd.to_datetime(fd['Date'],dayfirst=True,utc=True); fd=fd.dropna(subset=['date'])
 of=json.loads((ROOT/'data/raw/openfootball'/f'{season}-championship.json').read_text())
 # compare FD rows to OF by normalized pair, then pair+date
 of_rows=[{'date':pd.Timestamp(m['date'],tz='UTC').date(),'home':team(m['team1']),'away':team(m['team2'])} for m in of['matches']]
 for _,r in fd.iterrows():
  d=r.date.date(); h=team(r.HomeTeam); a=team(r.AwayTeam)
  same=[x for x in of_rows if x['home']==h and x['away']==a]
  if not same:
   same_team=[x for x in of_rows if x['home']==team(r.HomeTeam) and x['away']==team(r.AwayTeam)]
   reason='team_name_or_source_error' if same_team else 'unmatched_pair'
   delta=''
  elif any(x['date']==d for x in same): continue
  else:
   delta=min(abs((x['date']-d).days) for x in same); reason='date_shift_or_postponement'
  rows.append({'season':season,'date':str(d),'home_team':h,'away_team':a,'reason':reason,'date_delta_days':delta})
out=pd.DataFrame(rows); out.to_csv(ROOT/'data/interim/discrepancy_classified.csv',index=False)
print(out.groupby(['season','reason']).size().to_string())
print('\nexamples:'); print(out.head(30).to_string(index=False))
