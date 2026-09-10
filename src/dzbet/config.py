from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Phase0Config:
    steam_threshold: float = 0.10
    steam_window_seconds: int = 300
    confluence_hours: int = 6
    sentiment_threshold: float = -0.30
    min_bets: int = 100
    holdout_last_season: str | None = None

    def __post_init__(self) -> None:
        if self.steam_threshold <= 0 or self.steam_window_seconds <= 0:
            raise ValueError("steam threshold and window must be positive")
        if self.min_bets < 1:
            raise ValueError("min_bets must be positive")
