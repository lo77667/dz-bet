# Data provenance — Phase 0.3

## Scope

The target is EFL Championship (`E1`) for seasons 2019-20, 2020-21, 2021-22, 2022-23, 2023-24, 2024-25, 2025-26. The fixed split is Train: 2019-20 through 2022-23; Test: 2023-24 and 2024-25; Hold-out: 2025-26.

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
