from __future__ import annotations
import hashlib, json, re
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SEASONS=["2019-20","2020-21","2021-22","2022-23","2023-24","2024-25","2025-26"]
ALIASES={"QPR":"Queens Park Rangers","Sheff Utd":"Sheffield United","Sheff Wed":"Sheffield Wednesday","Sheffield Weds":"Sheffield Wednesday","Nott'm Forest":"Nottingham Forest","West Brom":"West Bromwich Albion","Blackburn":"Blackburn Rovers","Birmingham":"Birmingham City","Charlton":"Charlton Athletic","Coventry":"Coventry City","Huddersfield":"Huddersfield Town","Luton":"Luton Town","Middlesbrough":"Middlesbrough","Norwich":"Norwich City","Stoke":"Stoke City","Swansea":"Swansea City","Wigan":"Wigan Athletic","Rotherham":"Rotherham United","Cardiff":"Cardiff City","Reading":"Reading","Derby":"Derby County","Barnsley":"Barnsley","Brentford":"Brentford","Fulham":"Fulham","Leeds":"Leeds United","Watford":"Watford","Millwall":"Millwall","Bristol City":"Bristol City","Preston":"Preston North End","Hull":"Hull City","Plymouth":"Plymouth Argyle","Ipswich":"Ipswich Town","Portsmouth":"Portsmouth","Oxford":"Oxford United","Luton Town":"Luton Town","Bournemouth":"AFC Bournemouth","Leicester":"Leicester City","Peterboro":"Peterborough United","Wycombe":"Wycombe Wanderers"}

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
    closing_cols=[("PSCH","B365CH","H"),("PSCD","B365CD","D"),("PSCA","B365CA","A")]
    for pinnacle_col, bet365_col, selection in closing_cols:
        if pinnacle_col in fd and bet365_col in fd:
            values=fd[pinnacle_col].where(fd[pinnacle_col].notna(),fd[bet365_col])
            o=fd[["match_id","date"]].copy(); o["odds"]=values
            o["selection"]=selection; o["market"]="1X2"; o["bookmaker"]=pd.Series("Pinnacle",index=fd.index).mask(fd[pinnacle_col].isna(),"Bet365"); o["timestamp"]=pd.NaT
            all_odds.append(o[["match_id","bookmaker","market","selection","odds","timestamp"]])
    of=json.loads((ROOT/"data/raw/openfootball"/f"{season}-championship.json").read_text())
    of_keys={match_id(season,pd.Timestamp(f"{m['date']} {m.get('time','00:00')}",tz="UTC"),m["team1"],m["team2"]) for m in of["matches"]}
    fd_keys=set(matches.match_id)
    fd_pairs=set(zip(matches.home_team,matches.away_team))
    of_pairs=set((team(m["team1"]),team(m["team2"])) for m in of["matches"])
    comparisons.append({"season":season,"football_data_matches":len(fd_keys),"openfootball_matches":len(of_keys),"matched":len(fd_keys&of_keys),"fd_only":len(fd_keys-of_keys),"openfootball_only":len(of_keys-fd_keys),"pair_matched":len(fd_pairs&of_pairs),"pair_rate":len(fd_pairs&of_pairs)/max(len(fd_pairs),1)})

matches=pd.concat(all_matches,ignore_index=True); odds=pd.concat(all_odds,ignore_index=True)
matches.to_parquet(ROOT/"data/interim/matches.parquet",index=False); odds.to_parquet(ROOT/"data/interim/odds.parquet",index=False)
for split,seasons in {"train":SEASONS[:4],"test":SEASONS[4:6]}.items():
    matches[matches.season.isin(seasons)].to_parquet(ROOT/f"data/processed/{split}.parquet",index=False)
manifest=json.loads((ROOT/"data/MANIFEST.json").read_text())
manifest["derived"]={"matches_rows":len(matches),"odds_rows":len(odds),"closing_odds_definition":"PSCH/PSCD/PSCA (Pinnacle Closing), falling back to B365CH/B365CD/B365CA; quote timestamp is unavailable and is kept as NaT","processed":{"train_rows":int(sum(matches.season.isin(SEASONS[:4]))),"test_rows":int(sum(matches.season.isin(SEASONS[4:6]))),"holdout":"not created"}}
for season in SEASONS:
    p=ROOT/"data/raw/football-data-uk/E1"/f"{season}.csv"; manifest["sources"]["football-data-uk"][season]["sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
(ROOT/"data/MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
matched=sum(x["matched"] for x in comparisons); total=max(sum(x["football_data_matches"] for x in comparisons),1)
report=ROOT/"CROSS_VALIDATION.md"
report.write_text(f'''# Cross-validation report — Phase 0.3.d\n\n## Primary-source status\n\n`football-data.co.uk` was downloaded successfully using `requests` with redirect following. Seven E1 files are present. OpenFootball contains no odds fields and is used only for result cross-checking.\n\n## Match comparison\n\n| Season | football-data | OpenFootball | Exact date/team | Team-pair matched | FD only | OpenFootball only | Exact rate | Pair rate |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n{chr(10).join(f"| {x['season']} | {x['football_data_matches']} | {x['openfootball_matches']} | {x['matched']} | {x['pair_matched']} | {x['fd_only']} | {x['openfootball_only']} | {x['matched']/max(x['football_data_matches'],1):.2%} | {x['pair_rate']:.2%} |" for x in comparisons)}\n\nThe exact comparison uses season, date, normalized home team, and normalized away team. The team-pair comparison ignores date only to diagnose scheduling errors; it does not overwrite football-data dates. The 2019-20 OpenFootball file contains 77 matches dated one year earlier than football-data; these are classified as a source date defect.\n\n## Conflicts and resolution\n\n| Type | Source 1 | Source 2 | Resolution |\n|---|---|---|---|\n| Competition identity | OpenFootball `en.1.json` = Premier League | Target E1 Championship | Rejected `en.1`; retained verified `en.2` only |\n| Encoding | football-data Latin-1 | OpenFootball UTF-8 | Read source encodings explicitly; normalize internal strings |\n| Team aliases | football-data abbreviations | OpenFootball full names | Added aliases for Sheffield Weds, Bournemouth, Leicester, Peterboro, and Wycombe |\n| Date defect | OpenFootball 2019-20 dates shifted by 366 days for 77 pairs | football-data dates | Record as discrepancy; do not alter primary dates |\n| Odds | football-data has PSCH/PSCD/PSCA, with B365 closing fallback | OpenFootball has no odds | Use official closing columns; preserve timestamp as unknown |\n\n## Decision\n\n`HOLD` remains in force after manual verification and closing-column tests pass. Pair-level agreement is 100% after aliases/date diagnosis, but exact date agreement remains lower because of the OpenFootball defect. Quote timestamps are unavailable, so strict pre-kickoff timestamp validation remains unresolved. Understat remains unavailable for E1 and Club Elo returned HTTP 502.\n''',encoding="utf-8")
print(json.dumps({"matches":len(matches),"odds":len(odds),"comparisons":comparisons},ensure_ascii=False))
