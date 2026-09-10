# Cross-validation report — Phase 0.3

## Decision

`HOLD`. Cross-validation cannot pass because the required football-data.co.uk primary files and closing odds are not available in this run. No match-level equality claim is made.

## OpenFootball audit

The requested `en.1.json` path resolves to **English Premier League**, not Championship. To avoid mislabeled data, the approved OpenFootball source was downloaded using the correct Championship path `en.2.json` and stored as `*-championship.json`.

| Season | Championship records found | Structural check |
|---|---:|---|
| 2019-20 | 552 | PASS |
| 2020-21 | 552 | PASS |
| 2021-22 | 557 | PASS |
| 2022-23 | 557 | PASS |
| 2023-24 | 557 | PASS |
| 2024-25 | 557 | PASS |
| 2025-26 | 557 | PASS |

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
