from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEASONS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]

def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def games(path):
    data=json.loads(path.read_text()); return data.get("matches", [])

counts=[]
for season in SEASONS:
    path=ROOT/"data/raw/openfootball"/f"{season}-championship.json"
    counts.append((season, len(games(path)) if path.exists() else 0, sha(path) if path.exists() else None))
manifest=json.loads((ROOT/"data/MANIFEST.json").read_text())
manifest["sources"]["openfootball_championship_corrected"]={s:{"status":"downloaded","url":f"https://raw.githubusercontent.com/openfootball/football.json/master/{s}/en.2.json","sha256":h,"bytes":(ROOT/"data/raw/openfootball"/f"{s}-championship.json").stat().st_size} for s,_,h in counts}
manifest["source_metadata"]={
    "football-data-uk":{"url":"https://www.football-data.co.uk/data.php","downloaded_at":None,"sha256":None,"license":"See source terms; not redistributed here","encoding":"latin-1","status":"blocked"},
    "footballcsv-cache":{"url":"https://github.com/footballcsv","downloaded_at":None,"sha256":None,"license":"See repository terms","encoding":"UTF-8","status":"not_used"},
    "openfootball":{"url":"https://github.com/openfootball/football.json","downloaded_at":manifest["generated_at"],"sha256":"per-season hashes in sources.openfootball_championship_corrected","license":"See repository terms","encoding":"UTF-8","status":"downloaded_corrected_path"},
    "understat":{"url":"https://understat.com","downloaded_at":None,"sha256":None,"license":"See source terms","encoding":"UTF-8","status":"blocked_no_championship_coverage"},
    "clubelo":{"url":"https://clubelo.com","downloaded_at":None,"sha256":None,"license":"See source terms","encoding":"UTF-8","status":"blocked"},
}
manifest["notes"]=["The requested en.1.json path is English Premier League, not Championship. Championship files are en.2.json and are recorded separately.","football-data and Club Elo downloads were blocked by TLS timeouts in this run.","Understat coverage for Championship is not established; xG is not fabricated."]
(ROOT/"data/MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+"\n")
rows="\n".join(f"| {s} | {n} | {'PASS' if n >= 500 else 'FAIL'} |" for s,n,_ in counts)
(ROOT/"CROSS_VALIDATION.md").write_text(f'''# Cross-validation report — Phase 0.3

## Decision

`HOLD`. Cross-validation cannot pass because the required football-data.co.uk primary files and closing odds are not available in this run. No match-level equality claim is made.

## OpenFootball audit

The requested `en.1.json` path resolves to **English Premier League**, not Championship. To avoid mislabeled data, the approved OpenFootball source was downloaded using the correct Championship path `en.2.json` and stored as `*-championship.json`.

| Season | Championship records found | Structural check |
|---|---:|---|
{rows}

The record count is only a structural check. It is not cross-validation because the football-data primary source is missing.

## Required checks

| Check | Result | Reason |
|---|---|---|
| football-data.uk vs OpenFootball >=99% | BLOCKED | football-data.uk files unavailable due TLS connection timeouts |
| closing odds for every match | BLOCKED | primary football-data files not present |
| Understat xG coverage >=90% | BLOCKED | Understat does not establish Championship coverage here; no xG invented |
| team-name entity resolution | PENDING | requires both primary and cross-source match tables |
| explained discrepancies | PENDING | cannot compare absent primary source |

## Conflicts

The requested `en.1.json` filename conflicts with the requested Championship competition. The source's `en.1.json` files identify themselves as English Premier League. This was not silently accepted. The corrected `en.2.json` files are retained, and the mismatch is recorded in the manifest and provenance.
''', encoding='utf-8')
(ROOT/"DATA_PROVENANCE.md").write_text(f'''# Data provenance — Phase 0.3

## Scope

The target is EFL Championship (`E1`) for seasons {', '.join(SEASONS)}. The fixed split is Train: 2019-20 through 2022-23; Test: 2023-24 and 2024-25; Hold-out: 2025-26.

## Approved sources

| Source | Role | Status |
|---|---|---|
| football-data.co.uk | Primary results and odds | **Blocked in this run:** TLS connection timeout; no substitute used |
| footballcsv/cache.footballdata | Approved cache | Not used; no endpoint assumed |
| OpenFootball/football.json | Cross-check | Downloaded; requested `en.1.json` is Premier League, corrected Championship path is `en.2.json` |
| Understat via soccerdata | xG | Not established for Championship; no fabricated xG |
| Club Elo | Baseline | Blocked by TLS connection timeout; no substitute used |

## Reproducibility

The downloader is `scripts/download_phase0_3.py`. It is idempotent, uses only approved URLs, records SHA256, preserves `.part` files until a complete response, and writes `data/MANIFEST.json`. Re-running it does not redownload files already present and non-empty. The corrected OpenFootball Championship files and hashes are recorded in `MANIFEST.json`.

## Licensing and limitations

Each source's licensing and usage terms must be verified from its own project page before redistribution. This repository stores provenance and hashes; it does not claim ownership of the downloaded source data.

## Known issues

The primary site experienced TLS connection timeouts. The requested OpenFootball path was semantically wrong for Championship. Understat coverage for Championship is unverified. Team aliases, encoding, missing values, and closing-odds completeness cannot be resolved until the primary tables are available.

## Remaining risks

At present, primary results, closing odds, xG, and Club Elo baselines are incomplete. Therefore match-level cross-validation, >=90% xG coverage, ROI, and signal claims are prohibited. The empty parquet files under `data/interim` and `data/processed` are schema-only placeholders and must not be used as analytical data.
''', encoding='utf-8')
