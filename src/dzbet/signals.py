from __future__ import annotations

import pandas as pd

KEYWORDS = {"injury", "doubt", "angry", "tired", "family issue"}


def detect_steam_moves(odds: pd.DataFrame, threshold: float = 0.10, window_seconds: int = 300) -> pd.DataFrame:
    """Detect price moves per bookmaker/selection without looking at match outcomes."""
    rows = []
    for keys, group in odds.sort_values("timestamp").groupby(["match_id", "bookmaker", "market", "selection"]):
        group = group.reset_index(drop=True)
        for i in range(1, len(group)):
            delta_seconds = (group.loc[i, "timestamp"] - group.loc[i - 1, "timestamp"]).total_seconds()
            delta = float(group.loc[i, "odds"] - group.loc[i - 1, "odds"])
            if delta_seconds <= window_seconds and abs(delta) >= threshold:
                rows.append({"match_id": keys[0], "bookmaker": keys[1], "market": keys[2], "selection": keys[3], "timestamp": group.loc[i, "timestamp"], "previous_odds": group.loc[i - 1, "odds"], "current_odds": group.loc[i, "odds"], "delta": delta, "lag_seconds": delta_seconds})
    return pd.DataFrame(rows)


def team_stability_score(texts: pd.DataFrame) -> pd.DataFrame:
    """Score text sources deterministically; outcome linkage is intentionally separate."""
    required = {"team", "timestamp", "text", "source_type"}
    missing = required - set(texts.columns)
    if missing:
        raise ValueError(f"texts: missing columns: {sorted(missing)}")
    out = texts.copy()
    lowered = out["text"].fillna("").str.lower()
    out["keyword_hits"] = lowered.apply(lambda text: sorted(k for k in KEYWORDS if k in text))
    out["negative_signal"] = out["keyword_hits"].str.len().astype(float)
    out["source_weight"] = out["source_type"].map({"official": 0.5, "journalist": 1.0, "supporter": 1.0, "unknown": 0.5}).fillna(0.5)
    grouped = out.assign(weighted=out.negative_signal * out.source_weight).groupby(["team", "timestamp"], as_index=False).agg(weighted_negative=("weighted", "sum"), mentions=("text", "size"))
    grouped["team_stability_score"] = 1.0 / (1.0 + grouped["weighted_negative"])
    return grouped


def confluence_decision(a_positive: bool, b_positive: bool) -> str:
    if a_positive and b_positive:
        return "priority"
    if a_positive:
        return "caution"
    if b_positive:
        return "monitor"
    return "ignore"
