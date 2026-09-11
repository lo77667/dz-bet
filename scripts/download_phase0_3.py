#!/usr/bin/env python3
"""Download the approved Phase 0.3 Championship sources and build immutable metadata.

The script never invents missing data. A source that is unavailable is recorded as pending
in MANIFEST.json and the phase remains HOLD.
"""
from __future__ import annotations
import hashlib, json, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SEASONS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
FD_CODES = {s: s[2:4] + s[-2:] for s in SEASONS}
SOURCES = {
    "football-data-uk": "https://www.football-data.co.uk/mmz4281/{code}/E1.csv",
    "openfootball": "https://raw.githubusercontent.com/openfootball/football.json/master/{season}/en.2.json",
    "clubelo": "http://api.clubelo.com/{endyear}-06-30",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(url: str, destination: Path, minimum_bytes: int = 20, attempts: int = 3) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size >= minimum_bytes:
        return {"status": "cached", "url": url, "sha256": sha256(destination), "bytes": destination.stat().st_size}
    errors = []
    for attempt in range(1, attempts + 1):
        request = Request(url, headers={"User-Agent": "dz-bet-phase0.3/1.0"})
        try:
            with urlopen(request, timeout=60) as response:
                payload = response.read()
            if len(payload) < minimum_bytes:
                raise RuntimeError(f"response too small: {len(payload)} bytes")
            temporary = destination.with_suffix(destination.suffix + ".part")
            temporary.write_bytes(payload)
            temporary.replace(destination)
            time.sleep(1.0)
            return {"status": "downloaded", "url": url, "sha256": sha256(destination), "bytes": len(payload), "attempt": attempt}
        except Exception as error:
            errors.append(f"attempt {attempt}: {error}")
            if attempt < attempts:
                time.sleep(2 ** (attempt - 1))
    return {"status": "pending", "url": url, "error": "; ".join(errors), "attempts": attempts}


def main() -> int:
    raw = ROOT / "data" / "raw"
    for path in [raw / "football-data-uk" / "E1", raw / "footballcsv-cache" / "E1", raw / "openfootball", raw / "understat" / "E1", raw / "clubelo" / "E1", ROOT / "data" / "interim", ROOT / "data" / "processed"]:
        path.mkdir(parents=True, exist_ok=True)
    manifest = {"phase": "0.3", "generated_at": now(), "league": "E1", "seasons": SEASONS, "sources": {}, "splits": {"train": SEASONS[:4], "test": SEASONS[4:6], "holdout": SEASONS[6:]}}
    for season in SEASONS:
        code = FD_CODES[season]
        manifest["sources"].setdefault("football-data-uk", {})[season] = fetch(SOURCES["football-data-uk"].format(code=code), raw / "football-data-uk" / "E1" / f"{season}.csv")
        manifest["sources"].setdefault("openfootball", {})[season] = fetch(SOURCES["openfootball"].format(season=season), raw / "openfootball" / f"{season}-championship.json")
        endyear = int(season[:4]) + 1
        manifest["sources"].setdefault("clubelo", {})[season] = fetch(SOURCES["clubelo"].format(endyear=endyear), raw / "clubelo" / "E1" / f"{season}.csv")
    manifest["sources"]["footballcsv-cache"] = {"status": "pending", "note": "approved source; no automatic endpoint assumed"}
    manifest["sources"]["understat"] = {"status": "pending", "note": "requires soccerdata extraction; no fabricated xG files"}
    manifest["policy"] = {"holdout_immutable": True, "approved_sources_only": True, "raw_data_only": True}
    (ROOT / "data" / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": "data/MANIFEST.json", "phase": "0.3", "generated_at": manifest["generated_at"]}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
