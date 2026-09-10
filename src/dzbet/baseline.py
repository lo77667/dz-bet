from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

OUTCOMES = ("home", "draw", "away")

@dataclass
class PoissonModel:
    teams: list[str]
    attack: dict[str, float]
    defense: dict[str, float]
    home_advantage: float

    def probabilities(self, home: str, away: str, max_goals: int = 10) -> dict[str, float]:
        lh = math.exp(self.home_advantage + self.attack[home] - self.defense[away])
        la = math.exp(self.attack[away] - self.defense[home])
        matrix = np.outer(poisson.pmf(np.arange(max_goals + 1), lh), poisson.pmf(np.arange(max_goals + 1), la))
        return {"home": float(np.tril(matrix, -1).sum()), "draw": float(np.trace(matrix)), "away": float(np.triu(matrix, 1).sum())}


def fit_poisson(matches: pd.DataFrame) -> PoissonModel:
    teams = sorted(set(matches.home_team) | set(matches.away_team))
    idx = {team: i for i, team in enumerate(teams)}
    n = len(teams)
    # Parameters: attack[n], defense[n], home advantage. Sum-to-zero constraints stabilize scale.
    def unpack(x):
        attack = x[:n] - np.mean(x[:n])
        defense = x[n:2*n] - np.mean(x[n:2*n])
        return attack, defense, x[-1]
    def objective(x):
        attack, defense, home_adv = unpack(x)
        value = 0.0
        for row in matches.itertuples():
            lh = np.exp(home_adv + attack[idx[row.home_team]] - defense[idx[row.away_team]])
            la = np.exp(attack[idx[row.away_team]] - defense[idx[row.home_team]])
            value -= poisson.logpmf(row.home_goals, lh) + poisson.logpmf(row.away_goals, la)
        return float(value + 0.01 * np.sum(x * x))
    result = minimize(objective, np.zeros(2 * n + 1), method="L-BFGS-B")
    if not result.success:
        raise RuntimeError(f"Poisson optimization failed: {result.message}")
    attack, defense, home_adv = unpack(result.x)
    return PoissonModel(teams, dict(zip(teams, attack)), dict(zip(teams, defense)), float(home_adv))


def result_label(home_goals: int, away_goals: int) -> str:
    return "home" if home_goals > away_goals else "away" if home_goals < away_goals else "draw"


def backtest_baseline(train: pd.DataFrame, test: pd.DataFrame, odds: pd.DataFrame, bookmaker: str | None = None) -> dict:
    model = fit_poisson(train)
    rows = []
    selected_odds = odds[odds.bookmaker.eq(bookmaker)] if bookmaker else odds
    closing = (selected_odds.sort_values("timestamp").groupby(["match_id", "market", "selection"], as_index=False).tail(1))
    for row in test.itertuples():
        probs = model.probabilities(row.home_team, row.away_team)
        candidates = closing[(closing.match_id == row.match_id) & (closing.market == "1X2")]
        for odd in candidates.itertuples():
            if odd.selection not in probs:
                continue
            edge = probs[odd.selection] * odd.odds - 1.0
            if edge > 0:
                actual = result_label(row.home_goals, row.away_goals)
                pnl = odd.odds - 1.0 if actual == odd.selection else -1.0
                rows.append({"match_id": row.match_id, "selection": odd.selection, "probability": probs[odd.selection], "odds": odd.odds, "edge": edge, "pnl": pnl})
    bets = pd.DataFrame(rows)
    if bets.empty:
        return {"bets": 0, "roi": None, "profit": 0.0, "hit_rate": None, "note": "no positive-edge bets"}
    return {"bets": int(len(bets)), "roi": float(bets.pnl.sum() / len(bets)), "profit": float(bets.pnl.sum()), "hit_rate": float((bets.pnl > 0).mean())}
