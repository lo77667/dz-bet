from __future__ import annotations
import hashlib
from pathlib import Path
import pandas as pd


def assert_unique_match_ids(matches: pd.DataFrame) -> None:
    if matches.match_id.duplicated().any():
        raise ValueError("duplicate match_id")


def assert_no_missing_closing_odds(matches: pd.DataFrame, odds: pd.DataFrame) -> None:
    if matches.empty:
        return
    keys = odds["match_id"].drop_duplicates()
    missing = set(matches.match_id) - set(keys)
    if missing:
        raise ValueError(f"missing closing odds for {len(missing)} matches")


def assert_no_post_kickoff_odds(matches: pd.DataFrame, odds: pd.DataFrame) -> None:
    joined = odds.merge(matches[["match_id", "date"]], on="match_id", how="inner")
    if (joined.timestamp >= joined.date).any():
        raise ValueError("post-kickoff odds detected")


def xg_coverage(matches: pd.DataFrame, xg: pd.DataFrame) -> float:
    if matches.empty:
        return 0.0
    return float(matches.match_id.isin(set(xg.match_id)).mean())


def normalize_team_names(values: pd.Series) -> pd.Series:
    aliases = {"Sheff Wed": "Sheffield Wednesday", "Sheff Utd": "Sheffield United", "QPR": "Queens Park Rangers"}
    return values.astype(str).str.strip().replace(aliases)


def holdout_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
