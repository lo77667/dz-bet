# Phase 0.3.c — P0 results

## curl -L

`curl -L` succeeded for the corrected primary URL:

```text
https://www.football-data.co.uk/mmz4281/1920/E1.csv
HTTP/2 200
content-type: text/csv
content-length: 254740
```

The file contains E1 results and closing-price columns. It does not expose quote timestamps; the derived odds table preserves this as unknown rather than fabricating a pre-kickoff timestamp. The full diagnostic is stored in `data/raw/football-data-uk/E1/curl_L.log`.

## requests

`requests.get(..., allow_redirects=True, timeout=60)` also succeeded:

```text
status=200
url=https://football-data.co.uk/mmz4281/1920/E1.csv
bytes=254740
```

All seven E1 seasons were downloaded through `scripts/download_fd_requests.py` and recorded with SHA256 in `data/MANIFEST.json`.

## footballcsv/cache

The repository path was discovered and tested:

```text
https://raw.githubusercontent.com/footballcsv/cache.footballdata/master/2019-20/eng.2.csv
```

It downloaded successfully, but it contains only date, teams, full-time score, and half-time score. It contains no odds columns and cannot supply closing odds. The sample is retained under `data/raw/footballcsv-cache/E1/` with its hash in the manifest.

## OpenFootball odds

The first Championship match has fields:

```text
round, date, time, team1, team2, score
```

`odds_present = False`. OpenFootball is therefore results-only and cannot replace football-data for the odds requirement.

## P0 decision

```text
curl -L: PASS
requests redirect: PASS
Cache: PASS (results only; no odds)
OpenFootball odds: ABSENT
```

The project remains `HOLD` because cross-validation is below 99% for several seasons, quote timestamps are unavailable for strict pre-kickoff validation, and xG remains unavailable for E1. No ROI or signal claim is made.
