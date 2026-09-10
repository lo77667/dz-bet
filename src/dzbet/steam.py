from __future__ import annotations
import pandas as pd


def detect_steam_moves(odds: pd.DataFrame, threshold: float = 0.10, window_seconds: int = 300) -> pd.DataFrame:
    if threshold <= 0 or window_seconds <= 0:
        raise ValueError("threshold and window_seconds must be positive")
    rows = []
    keys = ["match_id", "bookmaker", "market", "selection"]
    for group_keys, group in odds.sort_values("timestamp").groupby(keys):
        group = group.reset_index(drop=True)
        for i in range(1, len(group)):
            seconds = (group.loc[i, "timestamp"] - group.loc[i - 1, "timestamp"]).total_seconds()
            delta = float(group.loc[i, "odds"] - group.loc[i - 1, "odds"])
            if 0 <= seconds <= window_seconds and abs(delta) >= threshold:
                rows.append(dict(zip(keys, group_keys), timestamp=group.loc[i, "timestamp"], previous_odds=group.loc[i - 1, "odds"], current_odds=group.loc[i, "odds"], delta=delta, lag_seconds=seconds))
    return pd.DataFrame(rows)
