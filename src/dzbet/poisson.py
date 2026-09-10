from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

@dataclass
class PoissonModel:
    teams: list[str]
    attack: dict[str, float]
    defense: dict[str, float]
    home_advantage: float

    def probabilities(self, home: str, away: str, max_goals: int = 10) -> dict[str, float]:
        lh = math.exp(self.home_advantage + self.attack[home] - self.defense[away])
        la = math.exp(self.attack[away] - self.defense[home])
        goals = np.arange(max_goals + 1)
        matrix = np.outer(poisson.pmf(goals, lh), poisson.pmf(goals, la))
        result = {"home": float(np.tril(matrix, -1).sum()), "draw": float(np.trace(matrix)), "away": float(np.triu(matrix, 1).sum())}
        total = sum(result.values())
        return {key: value / total for key, value in result.items()}


def fit_poisson(matches: pd.DataFrame) -> PoissonModel:
    teams = sorted(set(matches.home_team) | set(matches.away_team))
    index = {team: i for i, team in enumerate(teams)}
    n = len(teams)
    def unpack(params):
        return params[:n] - np.mean(params[:n]), params[n:2*n] - np.mean(params[n:2*n]), params[-1]
    def objective(params):
        attack, defense, home_advantage = unpack(params)
        value = 0.0
        for row in matches.itertuples():
            home_lambda = np.exp(home_advantage + attack[index[row.home_team]] - defense[index[row.away_team]])
            away_lambda = np.exp(attack[index[row.away_team]] - defense[index[row.home_team]])
            value -= poisson.logpmf(row.home_goals, home_lambda) + poisson.logpmf(row.away_goals, away_lambda)
        return float(value + 0.01 * np.sum(params * params))
    result = minimize(objective, np.zeros(2 * n + 1), method="L-BFGS-B")
    if not result.success:
        raise RuntimeError(f"Poisson optimization failed: {result.message}")
    attack, defense, home_advantage = unpack(result.x)
    return PoissonModel(teams, dict(zip(teams, attack)), dict(zip(teams, defense)), float(home_advantage))


def result_label(home_goals: int, away_goals: int) -> str:
    return "home" if home_goals > away_goals else "away" if home_goals < away_goals else "draw"
