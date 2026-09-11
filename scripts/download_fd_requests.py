from __future__ import annotations
import hashlib, json, time
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
SEASONS=["2019-20","2020-21","2021-22","2022-23","2023-24","2024-25","2025-26"]

def digest(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

results={}
for season in SEASONS:
    code=season[2:4]+season[-2:]
    url=f"https://www.football-data.co.uk/mmz4281/{code}/E1.csv"
    dest=ROOT/"data/raw/football-data-uk/E1"/f"{season}.csv"
    if dest.exists() and dest.stat().st_size > 1000:
        result={"status":"cached","url":url,"sha256":digest(dest),"bytes":dest.stat().st_size}
    else:
        errors=[]
        for attempt in range(1,4):
            try:
                response=requests.get(url, allow_redirects=True, timeout=60, headers={"User-Agent":"Mozilla/5.0 dz-bet/0.3c"})
                response.raise_for_status()
                if len(response.content) < 1000: raise RuntimeError(f"response too small: {len(response.content)}")
                part=dest.with_suffix(".csv.part"); part.write_bytes(response.content); part.replace(dest)
                result={"status":"downloaded","url":url,"resolved_url":response.url,"sha256":digest(dest),"bytes":dest.stat().st_size,"attempt":attempt}
                break
            except Exception as error:
                errors.append(f"attempt {attempt}: {type(error).__name__}: {error}")
                time.sleep(2**(attempt-1))
        else:
            result={"status":"pending","url":url,"error":"; ".join(errors)}
    results[season]=result
    print(season, result)

manifest_path=ROOT/"data/MANIFEST.json"
manifest=json.loads(manifest_path.read_text())
manifest["sources"]["football-data-uk"]=results
manifest["source_metadata"]["football-data-uk"].update({"status":"downloaded_via_requests" if all(x["status"] in {"downloaded","cached"} for x in results.values()) else "partially_blocked", "downloaded_at":datetime.now(timezone.utc).isoformat(), "encoding":"latin-1"})
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
