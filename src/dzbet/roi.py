from __future__ import annotations
import pandas as pd
from .poisson import fit_poisson, result_label


def closing_odds_before_kickoff(matches: pd.DataFrame, odds: pd.DataFrame, bookmaker: str | None = None) -> pd.DataFrame:
    selected = odds if bookmaker is None else odds[odds.bookmaker.eq(bookmaker)]
    joined = selected.merge(matches[["match_id", "date"]], on="match_id", how="inner")
    # A post-kickoff quote is not a closing price for a pre-match decision.
    joined = joined[joined.timestamp <= joined.date]
    return joined.sort_values("timestamp").groupby(["match_id", "market", "selection"], as_index=False).tail(1)


def backtest_roi(train: pd.DataFrame, test: pd.DataFrame, odds: pd.DataFrame, bookmaker: str | None = None) -> dict:
    model = fit_poisson(train)
    closing = closing_odds_before_kickoff(test, odds, bookmaker)
    rows = []
    for row in test.itertuples():
        probabilities = model.probabilities(row.home_team, row.away_team)
        candidates = closing[(closing.match_id == row.match_id) & (closing.market == "1X2")]
        for quote in candidates.itertuples():
            if quote.selection not in probabilities:
                continue
            edge = probabilities[quote.selection] * quote.odds - 1.0
            if edge > 0:
                actual = result_label(row.home_goals, row.away_goals)
                pnl = quote.odds - 1.0 if actual == quote.selection else -1.0
                rows.append({"match_id": row.match_id, "selection": quote.selection, "odds": quote.odds, "edge": edge, "pnl": pnl})
    bets = pd.DataFrame(rows)
    if bets.empty:
        return {"bets": 0, "roi": None, "profit": 0.0, "hit_rate": None, "note": "no positive-edge bets"}
    return {"bets": int(len(bets)), "roi": float(bets.pnl.sum() / len(bets)), "profit": float(bets.pnl.sum()), "hit_rate": float((bets.pnl > 0).mean())}
