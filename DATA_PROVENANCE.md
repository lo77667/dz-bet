# Data provenance — Phase 0.3

## Scope

The target is EFL Championship (`E1`) for seasons 2019-20, 2020-21, 2021-22, 2022-23, 2023-24, 2024-25, 2025-26. The fixed split is Train: 2019-20 through 2022-23; Test: 2023-24 and 2024-25; Hold-out: 2025-26.

## Approved sources

| Source | Role | Status |
|---|---|---|
| football-data.co.uk | Primary results and odds | **Downloaded successfully via requests** for all seven E1 seasons; Latin-1 |
| footballcsv/cache.footballdata | Approved cache | Sample downloaded from `2019-20/eng.2.csv`; results-only, no odds |
| OpenFootball/football.json | Cross-check | Downloaded from `en.2.json`; verified metadata and 24 teams per season |
| Understat via soccerdata | xG | Attempted; `ENG-Championship` is rejected as unsupported by soccerdata/Understat |
| Club Elo | Baseline | Attempted over HTTP; returned HTTP 502 Bad Gateway |

## Reproducibility

The downloader is `scripts/download_phase0_3.py`; the requests-based E1 execution is captured in `scripts/download_fd_requests.py`. Both use approved URLs, record SHA256, preserve `.part` files until a complete response, and update `data/MANIFEST.json`. Re-running does not redownload files already present and non-empty. The corrected OpenFootball Championship files and all seven primary E1 hashes are recorded in `MANIFEST.json`.

## Licensing and limitations

Each source's licensing and usage terms must be verified from its own project page before redistribution. This repository stores provenance and hashes; it does not claim ownership of the downloaded source data.

## Known issues

The initial urllib/curl path stalled after a redirect, but `curl -L` and Python `requests` both succeeded. The requested OpenFootball path was semantically wrong for Championship. The Understat probe returned `ValueError: Invalid league 'ENG-Championship'`; valid soccerdata leagues listed only the five major leagues. The Club Elo HTTP probe returned `502 Bad Gateway`. Cross-source matching remains below 99% in several seasons and requires alias/date discrepancy review.

## Remaining risks

Primary results and football-data closing columns are now present. xG and Club Elo remain unavailable. Cross-validation is below 99% for several seasons, so ROI and signal claims remain prohibited. `data/interim/matches.parquet`, `data/interim/odds.parquet`, and processed Train/Test files contain derived data; the hold-out file is intentionally absent and must remain absent until final data authorization.
