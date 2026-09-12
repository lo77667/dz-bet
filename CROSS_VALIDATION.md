# Cross-validation report — Phase 0.3.d

## Primary-source status

`football-data.co.uk` was downloaded successfully using `requests` with redirect following. Seven E1 files are present. OpenFootball contains no odds fields and is used only for result cross-checking.

## Match comparison

| Season | football-data | OpenFootball | Exact date/team | Team-pair matched | FD only | OpenFootball only | Exact rate | Pair rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019-20 | 552 | 552 | 475 | 552 | 77 | 77 | 86.05% | 100.00% |
| 2020-21 | 552 | 552 | 552 | 552 | 0 | 0 | 100.00% | 100.00% |
| 2021-22 | 552 | 557 | 552 | 552 | 0 | 5 | 100.00% | 100.00% |
| 2022-23 | 552 | 557 | 552 | 552 | 0 | 5 | 100.00% | 100.00% |
| 2023-24 | 552 | 557 | 552 | 552 | 0 | 5 | 100.00% | 100.00% |
| 2024-25 | 552 | 557 | 552 | 552 | 0 | 5 | 100.00% | 100.00% |
| 2025-26 | 552 | 557 | 552 | 552 | 0 | 5 | 100.00% | 100.00% |

The exact comparison uses season, date, normalized home team, and normalized away team. The team-pair comparison ignores date only to diagnose scheduling errors; it does not overwrite football-data dates. The 2019-20 OpenFootball file contains 77 matches dated one year earlier than football-data; these are classified as a source date defect.

## Conflicts and resolution

| Type | Source 1 | Source 2 | Resolution |
|---|---|---|---|
| Competition identity | OpenFootball `en.1.json` = Premier League | Target E1 Championship | Rejected `en.1`; retained verified `en.2` only |
| Encoding | football-data Latin-1 | OpenFootball UTF-8 | Read source encodings explicitly; normalize internal strings |
| Team aliases | football-data abbreviations | OpenFootball full names | Added aliases for Sheffield Weds, Bournemouth, Leicester, Peterboro, and Wycombe |
| Date defect | OpenFootball 2019-20 dates shifted by 366 days for 77 pairs | football-data dates | Record as discrepancy; do not alter primary dates |
| Odds | football-data has PSCH/PSCD/PSCA, with B365 closing fallback | OpenFootball has no odds | Use official closing columns; preserve timestamp as unknown |

## Decision

`HOLD` remains in force after manual verification and closing-column tests pass. Pair-level agreement is 100% after aliases/date diagnosis, but exact date agreement remains lower because of the OpenFootball defect. Quote timestamps are unavailable, so strict pre-kickoff timestamp validation remains unresolved. Understat remains unavailable for E1 and Club Elo returned HTTP 502.
