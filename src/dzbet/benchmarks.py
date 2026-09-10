from __future__ import annotations
import pandas as pd
from .poisson import result_label


def base_rate_probabilities(train: pd.DataFrame) -> dict[str, float]:
    labels = train.apply(lambda r: result_label(r.home_goals, r.away_goals), axis=1)
    counts = labels.value_counts().reindex(["home", "draw", "away"], fill_value=0).astype(float)
    # Laplace smoothing keeps every outcome possible without using future data.
    smoothed = counts + 1.0
    return (smoothed / smoothed.sum()).to_dict()


def base_rate_roi(train: pd.DataFrame, test: pd.DataFrame, odds: pd.DataFrame) -> dict:
    probabilities = base_rate_probabilities(train)
    rows = []
    for row in test.itertuples():
        candidates = odds[(odds.match_id == row.match_id) & (odds.market == "1X2")]
        for quote in candidates.itertuples():
            if quote.selection in probabilities and probabilities[quote.selection] * quote.odds > 1:
                actual = result_label(row.home_goals, row.away_goals)
                rows.append(quote.odds - 1 if actual == quote.selection else -1)
    return {"bets": len(rows), "roi": sum(rows) / len(rows) if rows else None}
