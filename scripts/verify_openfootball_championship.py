#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEASONS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
KNOWN = {"Leeds United FC", "Norwich City FC", "Watford FC", "Queens Park Rangers FC", "Middlesbrough FC", "Coventry City FC", "Bristol City FC", "Sunderland AFC", "Derby County FC", "Sheffield Wednesday FC", "Sheffield United FC", "West Bromwich Albion FC", "Blackburn Rovers FC", "Preston North End FC", "Stoke City FC", "Cardiff City FC", "Swansea City FC", "Millwall FC", "Luton Town FC", "Hull City FC", "Rotherham United FC", "Plymouth Argyle FC", "Birmingham City FC", "Portsmouth FC", "Oxford United FC", "Reading FC", "Wigan Athletic FC", "Bolton Wanderers FC", "Ipswich Town FC", "Huddersfield Town FC"}

def norm(name: str) -> str:
    name = re.sub(r"\s+(FC|AFC)$", "", name.strip())
    return {"QPR": "Queens Park Rangers", "Sheffield Wed": "Sheffield Wednesday", "Sheff Wed": "Sheffield Wednesday", "Sheff Utd": "Sheffield United"}.get(name, name)

rows=[]
for season in SEASONS:
    path=ROOT/"data/raw/openfootball"/f"{season}-championship.json"
    data=json.loads(path.read_text(encoding="utf-8"))
    teams=sorted({norm(team) for match in data["matches"] for team in (match["team1"], match["team2"])})
    known={norm(team) for team in KNOWN}
    metadata_ok="championship" in data.get("name", "").lower()
    rows.append({"season":season,"name":data.get("name"),"matches":len(data["matches"]),"teams":len(teams),"known_overlap":len(set(teams)&known),"metadata_ok":metadata_ok,"team_names":teams})
report=ROOT/"OPENFOOTBALL_CHAMPIONSHIP_VERIFY.md"
with report.open("w", encoding="utf-8") as out:
    out.write("# OpenFootball Championship structural verification\n\n")
    out.write("| Season | Metadata | Matches | Teams | Known-team overlap | Result |\n|---|---|---:|---:|---:|---|\n")
    for r in rows:
        result = r["metadata_ok"] and r["teams"] == 24 and r["known_overlap"] >= 12
        out.write(f"| {r['season']} | {r['name']} | {r['matches']} | {r['teams']} | {r['known_overlap']} | {'PASS' if result else 'FAIL'} |\n")
    out.write("\nThe check uses the source metadata, 24-team season structure, and overlap with a maintained historical Championship team set. It is a structural source-identity check, not cross-validation against football-data.uk.\n")
for r in rows:
    if not (r["metadata_ok"] and r["teams"] == 24):
        raise SystemExit(f"Championship verification failed: {r['season']}")
print(f"verified {len(rows)} seasons")
