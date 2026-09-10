from __future__ import annotations
from .config import Phase0Config

def checks(*, holdout_used_for_tuning: bool, odds_are_closing: bool, timestamp_aligned: bool, sample_size: int, config: Phase0Config) -> list[str]:
    failures = []
    if holdout_used_for_tuning:
        failures.append("hold-out was used for tuning")
    if not odds_are_closing:
        failures.append("closing odds are not proven")
    if not timestamp_aligned:
        failures.append("signals are not timestamp-aligned")
    if sample_size < config.min_bets:
        failures.append(f"sample size {sample_size} is below minimum {config.min_bets}")
    return failures
