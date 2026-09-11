from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"data/MANIFEST.json"; d=json.loads(p.read_text())
# Remove the rejected Premier League source and keep only the verified Championship path.
d["sources"].pop("openfootball_championship_corrected", None)
d["sources"]["openfootball"]={}
for season, item in d["sources"].get("football-data-uk", {}).items():
    item["url"] = f"https://www.football-data.co.uk/mmz4281/{season[2:4]}{season[-2:]}/E1.csv"
for season, item in d["sources"].get("clubelo", {}).items():
    item["url"] = f"http://api.clubelo.com/{int(season[:4]) + 1}-06-30"
for season in d["seasons"]:
    path=ROOT/"data/raw/openfootball"/f"{season}-championship.json"
    h=hashlib.sha256(path.read_bytes()).hexdigest()
    d["sources"]["openfootball"][season]={"status":"downloaded","url":f"https://raw.githubusercontent.com/openfootball/football.json/master/{season}/en.2.json","downloaded_at":d["generated_at"],"sha256":h,"bytes":path.stat().st_size,"encoding":"UTF-8"}
probe=json.loads((ROOT/"data/understat_probe.json").read_text())
d["source_metadata"]["understat"].update({"status":probe["status"],"checked_at":probe["checked_at"],"error":probe.get("error")})
d["source_metadata"]["clubelo"].update({"url":"http://api.clubelo.com/{endyear}-06-30","status":"blocked_http_502","error":"curl HTTP/1.1 502 Bad Gateway"})
d["source_metadata"]["football-data-uk"].update({"status":"blocked_tls_or_redirect_timeout","diagnostic":"data/raw/football-data-uk/E1/curl_diagnostic.txt","correct_url_pattern":"https://www.football-data.co.uk/mmz4281/{YYYY}/E1.csv"})
d["notes"]=["OpenFootball en.1.json was rejected because it is English Premier League; only verified en.2.json Championship files remain in sources.openfootball.","The source identity check found seven seasons with Championship metadata and 24 unique teams.","football-data curl diagnostic shows HTTP redirect to https://football-data.co.uk followed by a connection stall in this environment.","Understat was attempted via soccerdata and rejected ENG-Championship as unsupported; no xG was fabricated.","Club Elo was retried over HTTP and returned HTTP 502 Bad Gateway."]
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
