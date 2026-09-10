import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"data/MANIFEST.json"
d=json.loads(p.read_text())
for season, item in d["sources"]["football-data-uk"].items():
    code=season[:2]+season[-2:]
    item["url"]=f"https://www.football-data.co.uk/mmz4281/{code}/E1.csv"
p.write_text(json.dumps(d, indent=2, ensure_ascii=False)+"\n")
