# Cross-validation report — Phase 0.3.c

## Primary-source status

`football-data.co.uk` was downloaded successfully using `requests` with redirect following. Seven E1 files are present. OpenFootball contains no odds fields and is used only for result cross-checking.

## Match comparison

| Season | football-data | OpenFootball | Matched | FD only | OpenFootball only | Match rate |
|---|---:|---:|---:|---:|---:|---:|
| 2019-20 | 552 | 552 | 436 | 116 | 116 | 78.99% |
| 2020-21 | 552 | 552 | 420 | 132 | 132 | 76.09% |
| 2021-22 | 552 | 557 | 462 | 90 | 95 | 83.70% |
| 2022-23 | 552 | 557 | 552 | 0 | 5 | 100.00% |
| 2023-24 | 552 | 557 | 462 | 90 | 95 | 83.70% |
| 2024-25 | 552 | 557 | 506 | 46 | 51 | 91.67% |
| 2025-26 | 552 | 557 | 462 | 90 | 95 | 83.70% |

The comparison uses season, date, normalized home team, and normalized away team. Any rate below 99% remains a HOLD condition and is not silently treated as agreement.

## Conflicts and resolution

| Type | Source 1 | Source 2 | Resolution |
|---|---|---|---|
| Competition identity | OpenFootball `en.1.json` = Premier League | Target E1 Championship | Rejected `en.1`; retained verified `en.2` only |
| Encoding | football-data Latin-1 | OpenFootball UTF-8 | Read source encodings explicitly; normalize internal strings |
| Team aliases | football-data abbreviations | OpenFootball full names | Alias map in `build_phase03_data.py`; unresolved names remain visible in counts |
| Odds | football-data has closing columns | OpenFootball has no odds | Closing odds remain football-data-only |

## Decision

`HOLD` until every match has valid closing odds and the cross-source match rate is at least 99%. Understat remains unavailable for E1 and Club Elo returned HTTP 502.
