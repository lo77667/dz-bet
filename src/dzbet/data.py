from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd

MATCH_COLUMNS = ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "season"]
ODDS_COLUMNS = ["match_id", "bookmaker", "market", "selection", "odds", "timestamp"]


@dataclass(frozen=True)
class DataBundle:
    matches: pd.DataFrame
    odds: pd.DataFrame


def _require(df: pd.DataFrame, columns: list[str], name: str) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{name}: missing required columns: {', '.join(missing)}")


def load_matches(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    _require(df, MATCH_COLUMNS, "matches")
    df = df[MATCH_COLUMNS].copy()
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="raise")
    for col in ["home_goals", "away_goals"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
        if (df[col] < 0).any():
            raise ValueError(f"matches: {col} cannot be negative")
    if df["match_id"].duplicated().any():
        raise ValueError("matches: match_id must be unique")
    if df[["home_team", "away_team"]].isna().any().any():
        raise ValueError("matches: team names cannot be null")
    return df.sort_values("date").reset_index(drop=True)


def load_odds(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    _require(df, ODDS_COLUMNS, "odds")
    df = df[ODDS_COLUMNS].copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="raise")
    df["odds"] = pd.to_numeric(df["odds"], errors="raise")
    if (df["odds"] <= 1.0).any():
        raise ValueError("odds: decimal odds must be greater than 1.0")
    if df[["match_id", "bookmaker", "market", "selection"]].isna().any().any():
        raise ValueError("odds: key columns cannot be null")
    return df.sort_values("timestamp").reset_index(drop=True)


def load_bundle(matches_path: str | Path, odds_path: str | Path) -> DataBundle:
    matches, odds = load_matches(matches_path), load_odds(odds_path)
    unknown = set(odds["match_id"]) - set(matches["match_id"])
    if unknown:
        raise ValueError(f"odds: unknown match_id values: {sorted(unknown)[:5]}")
    return DataBundle(matches, odds)
