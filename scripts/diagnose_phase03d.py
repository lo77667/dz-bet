from __future__ import annotations
import json, hashlib, re
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
SEASONS=['2019-20','2020-21','2021-22','2022-23','2023-24','2024-25','2025-26']
ALIASES={"QPR":"Queens Park Rangers","Sheff Utd":"Sheffield United","Sheff Wed":"Sheffield Wednesday","Sheffield Weds":"Sheffield Wednesday","Nott'm Forest":"Nottingham Forest","West Brom":"West Bromwich Albion","Blackburn":"Blackburn Rovers","Birmingham":"Birmingham City","Charlton":"Charlton Athletic","Coventry":"Coventry City","Huddersfield":"Huddersfield Town","Luton":"Luton Town","Norwich":"Norwich City","Stoke":"Stoke City","Swansea":"Swansea City","Wigan":"Wigan Athletic","Rotherham":"Rotherham United","Cardiff":"Cardiff City","Derby":"Derby County","Leeds":"Leeds United","Watford":"Watford","Millwall":"Millwall","Bristol City":"Bristol City","Preston":"Preston North End","Hull":"Hull City","Plymouth":"Plymouth Argyle","Ipswich":"Ipswich Town","Oxford":"Oxford United","Middlesbrough":"Middlesbrough","Bournemouth":"AFC Bournemouth","Leicester":"Leicester City","Peterboro":"Peterborough United","Wycombe":"Wycombe Wanderers"}
def team(x):
 x=re.sub(r'\s+(FC|AFC)$','',str(x).strip()); return ALIASES.get(x,x)
def key(season,date,h,a): return f'{season}|{date.date().isoformat()}|{team(h)}|{team(a)}'
def ft_score(score):
 if isinstance(score,dict): return score.get('ft',[None,None])
 return score if isinstance(score,list) else [None,None]
rows=[]
for season in SEASONS:
 fd=pd.read_csv(ROOT/'data/raw/football-data-uk/E1'/f'{season}.csv',encoding='latin-1')
 fd['date']=pd.to_datetime(fd['Date'],dayfirst=True,utc=True)
 fd=fd.dropna(subset=['date'])
 fd_keys={key(season,d,h,a):(season,d.date().isoformat(),team(h),team(a),int(g1),int(g2),str(r)) for d,h,a,g1,g2,r in zip(fd.date,fd.HomeTeam,fd.AwayTeam,fd.FTHG,fd.FTAG,fd.FTR)}
 of=json.loads((ROOT/'data/raw/openfootball'/f'{season}-championship.json').read_text())
 of_keys={key(season,pd.Timestamp(m['date'],tz='UTC'),m['team1'],m['team2']):(season,m['date'],team(m['team1']),team(m['team2']),ft_score(m['score'])[0],ft_score(m['score'])[1],None) for m in of['matches']}
 for k,v in fd_keys.items():
  if k not in of_keys: rows.append({'season':season,'match_id':k,'date':v[1],'home_team':v[2],'away_team':v[3],'fd_home_goals':v[4],'fd_away_goals':v[5],'fd_result':v[6],'of_status':'missing','reason':'not found by exact date/team key'})
 for k,v in of_keys.items():
  if k not in fd_keys: rows.append({'season':season,'match_id':k,'date':v[1],'home_team':v[2],'away_team':v[3],'fd_home_goals':None,'fd_away_goals':None,'fd_result':None,'of_status':'openfootball_only','reason':'not found by exact date/team key'})
df=pd.DataFrame(rows); df.to_csv(ROOT/'data/interim/cross_validation_discrepancies.csv',index=False)
# deterministic 10-match sample: evenly spaced across 2024-25 in source order
fd=pd.read_csv(ROOT/'data/raw/football-data-uk/E1/2024-25.csv',encoding='latin-1')
fd=fd.dropna(subset=['Date']).reset_index(drop=True)
indices=[int(round(i*(len(fd)-1)/9)) for i in range(10)]
sample=fd.iloc[indices][['Date','Time','HomeTeam','AwayTeam','FTHG','FTAG','FTR']].copy(); sample.insert(0,'sample_id',range(1,11)); sample.to_csv(ROOT/'data/interim/manual_validation_sample_2024_25.csv',index=False)
summary=df.groupby(['season','of_status']).size().unstack(fill_value=0).reset_index(); summary.to_csv(ROOT/'data/interim/discrepancy_summary.csv',index=False)
print('discrepancies=',len(df)); print(summary.to_string(index=False)); print('sample='); print(sample.to_string(index=False))
