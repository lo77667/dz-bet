from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
result={"checked_at":datetime.now(timezone.utc).isoformat(),"source":"Understat via soccerdata","league":"ENG-Championship","status":"blocked"}
try:
    import soccerdata as sd
    understat=sd.Understat(leagues="ENG-Championship", seasons=["1920", "2020", "2122", "2223", "2324", "2425", "2526"], no_cache=False)
    frame=understat.read_team_match_stats()
    result.update({"status":"downloaded","rows":int(frame.shape[0]),"columns":list(frame.columns)})
except Exception as error:
    result["error"]=f"{type(error).__name__}: {error}"
(ROOT/"data/understat_probe.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n")
print(json.dumps(result, ensure_ascii=False))
