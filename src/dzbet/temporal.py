from __future__ import annotations
import re
import pandas as pd

SEASON_PATTERN = re.compile(r"^(\d{4})-(\d{4})$")


def validate_season_boundaries(matches: pd.DataFrame) -> None:
    required = {"match_id", "date", "season"}
    missing = required - set(matches.columns)
    if missing:
        raise ValueError(f"matches: missing temporal columns: {sorted(missing)}")
    if matches.match_id.duplicated().any():
        raise ValueError("matches: match_id appears more than once")
    for season, group in matches.groupby("season"):
        match = SEASON_PATTERN.match(str(season))
        if not match or int(match.group(2)) != int(match.group(1)) + 1:
            raise ValueError(f"invalid sporting season label: {season}")
        start = pd.Timestamp(f"{match.group(1)}-07-01", tz="UTC")
        end = pd.Timestamp(f"{match.group(2)}-07-01", tz="UTC")
        if (group.date < start).any() or (group.date >= end).any():
            raise ValueError(f"match date falls outside declared season {season}")


def split_seasons(matches: pd.DataFrame, holdout_season: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    validate_season_boundaries(matches)
    seasons = sorted(matches.season.astype(str).unique())
    if holdout_season not in seasons:
        raise ValueError(f"holdout season {holdout_season} is absent")
    holdout_index = seasons.index(holdout_season)
    if holdout_index < 2:
        raise ValueError("at least two seasons before hold-out are required")
    test_season = seasons[holdout_index - 1]
    train_seasons = set(seasons[:holdout_index - 1])
    train = matches[matches.season.astype(str).isin(train_seasons)].copy()
    test = matches[matches.season.astype(str).eq(test_season)].copy()
    holdout = matches[matches.season.astype(str).eq(holdout_season)].copy()
    if set(train.match_id) & (set(test.match_id) | set(holdout.match_id)):
        raise ValueError("temporal split overlap detected")
    return train, test, holdout
