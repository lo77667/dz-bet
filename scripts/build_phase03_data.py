from __future__ import annotations
import hashlib, json, re
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SEASONS=["2019-20","2020-21","2021-22","2022-23","2023-24","2024-25","2025-26"]
ALIASES={"QPR":"Queens Park Rangers","Sheff Utd":"Sheffield United","Sheff Wed":"Sheffield Wednesday","Nott'm Forest":"Nottingham Forest","West Brom":"West Bromwich Albion","Blackburn":"Blackburn Rovers","Birmingham":"Birmingham City","Charlton":"Charlton Athletic","Coventry":"Coventry City","Huddersfield":"Huddersfield Town","Luton":"Luton Town","Middlesbrough":"Middlesbrough","Norwich":"Norwich City","Stoke":"Stoke City","Swansea":"Swansea City","Wigan":"Wigan Athletic","Rotherham":"Rotherham United","Cardiff":"Cardiff City","Reading":"Reading","Derby":"Derby County","Barnsley":"Barnsley","Brentford":"Brentford","Fulham":"Fulham","Leeds":"Leeds United","Watford":"Watford","Millwall":"Millwall","Bristol City":"Bristol City","Preston":"Preston North End","Hull":"Hull City","Plymouth":"Plymouth Argyle","Ipswich":"Ipswich Town","Portsmouth":"Portsmouth","Oxford":"Oxford United","Luton Town":"Luton Town"}

def team(value):
    value=str(value).strip()
    value=re.sub(r"\s+(FC|AFC)$", "", value)
    return ALIASES.get(value, value)

def match_id(season,date,home,away):
    return f"{season}|{date.date().isoformat()}|{team(home)}|{team(away)}"

all_matches=[]; all_odds=[]; comparisons=[]
for season in SEASONS:
    path=ROOT/"data/raw/football-data-uk/E1"/f"{season}.csv"
    fd=pd.read_csv(path, encoding="latin-1")
    fd["date"]=pd.to_datetime(fd["Date"], dayfirst=True, errors="coerce", utc=True)
    fd=fd.dropna(subset=["date","HomeTeam","AwayTeam"]).copy()
    fd["home_team"]=fd["HomeTeam"].map(team); fd["away_team"]=fd["AwayTeam"].map(team); fd["season"]=season
    fd["match_id"]=[match_id(season,d,h,a) for d,h,a in zip(fd.date,fd.HomeTeam,fd.AwayTeam)]
    matches=fd[["match_id","date","home_team","away_team","FTHG","FTAG","FTR","season"]].rename(columns={"FTHG":"home_goals","FTAG":"away_goals","FTR":"result"})
    all_matches.append(matches)
    odds_cols=[("AvgCH","H"),("AvgCD","D"),("AvgCA","A")]
    for col,selection in odds_cols:
        if col in fd:
            o=fd[["match_id","date",col]].rename(columns={col:"odds"})
            o["selection"]=selection; o["market"]="1X2"; o["bookmaker"]="football-data-average"; o["timestamp"]=pd.NaT
            all_odds.append(o[["match_id","bookmaker","market","selection","odds","timestamp"]])
    of=json.loads((ROOT/"data/raw/openfootball"/f"{season}-championship.json").read_text())
    of_keys={match_id(season,pd.Timestamp(f"{m['date']} {m.get('time','00:00')}",tz="UTC"),m["team1"],m["team2"]) for m in of["matches"]}
    fd_keys=set(matches.match_id)
    comparisons.append({"season":season,"football_data_matches":len(fd_keys),"openfootball_matches":len(of_keys),"matched":len(fd_keys&of_keys),"fd_only":len(fd_keys-of_keys),"openfootball_only":len(of_keys-fd_keys)})

matches=pd.concat(all_matches,ignore_index=True); odds=pd.concat(all_odds,ignore_index=True)
matches.to_parquet(ROOT/"data/interim/matches.parquet",index=False); odds.to_parquet(ROOT/"data/interim/odds.parquet",index=False)
for split,seasons in {"train":SEASONS[:4],"test":SEASONS[4:6]}.items():
    matches[matches.season.isin(seasons)].to_parquet(ROOT/f"data/processed/{split}.parquet",index=False)
manifest=json.loads((ROOT/"data/MANIFEST.json").read_text())
manifest["derived"]={"matches_rows":len(matches),"odds_rows":len(odds),"closing_odds_definition":"AvgCH/AvgCD/AvgCA from football-data.co.uk; quote timestamp is unavailable in the source and is therefore kept as NaT","processed":{"train_rows":int(sum(matches.season.isin(SEASONS[:4]))),"test_rows":int(sum(matches.season.isin(SEASONS[4:6]))),"holdout":"not created"}}
for season in SEASONS:
    p=ROOT/"data/raw/football-data-uk/E1"/f"{season}.csv"; manifest["sources"]["football-data-uk"][season]["sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
(ROOT/"data/MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
matched=sum(x["matched"] for x in comparisons); total=max(sum(x["football_data_matches"] for x in comparisons),1)
report=ROOT/"CROSS_VALIDATION.md"
report.write_text(f'''# Cross-validation report — Phase 0.3.c\n\n## Primary-source status\n\n`football-data.co.uk` was downloaded successfully using `requests` with redirect following. Seven E1 files are present. OpenFootball contains no odds fields and is used only for result cross-checking.\n\n## Match comparison\n\n| Season | football-data | OpenFootball | Matched | FD only | OpenFootball only | Match rate |\n|---|---:|---:|---:|---:|---:|---:|\n{chr(10).join(f"| {x['season']} | {x['football_data_matches']} | {x['openfootball_matches']} | {x['matched']} | {x['fd_only']} | {x['openfootball_only']} | {x['matched']/max(x['football_data_matches'],1):.2%} |" for x in comparisons)}\n\nThe comparison uses season, date, normalized home team, and normalized away team. Any rate below 99% remains a HOLD condition and is not silently treated as agreement.\n\n## Conflicts and resolution\n\n| Type | Source 1 | Source 2 | Resolution |\n|---|---|---|---|\n| Competition identity | OpenFootball `en.1.json` = Premier League | Target E1 Championship | Rejected `en.1`; retained verified `en.2` only |\n| Encoding | football-data Latin-1 | OpenFootball UTF-8 | Read source encodings explicitly; normalize internal strings |\n| Team aliases | football-data abbreviations | OpenFootball full names | Alias map in `build_phase03_data.py`; unresolved names remain visible in counts |\n| Odds | football-data has closing columns | OpenFootball has no odds | Closing odds remain football-data-only |\n\n## Decision\n\n`HOLD` until every match has valid closing odds and the cross-source match rate is at least 99%. Understat remains unavailable for E1 and Club Elo returned HTTP 502.\n''',encoding="utf-8")
print(json.dumps({"matches":len(matches),"odds":len(odds),"comparisons":comparisons},ensure_ascii=False))
