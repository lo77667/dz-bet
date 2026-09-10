from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
import json

@dataclass(frozen=True)
class GateConfig:
    steam_threshold: float = 0.10
    steam_window_seconds: int = 300
    sentiment_threshold: float = -0.30
    confluence_hours: int = 6
    min_bets: int = 100
    holdout_last_season: str | None = None


def devil_advocate_checks(*, holdout_used_for_tuning: bool, odds_are_closing: bool, timestamp_aligned: bool, sample_size: int, config: GateConfig) -> list[str]:
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


def build_gate_report(config: GateConfig, path_a: dict[str, Any], path_b: dict[str, Any], confluence: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    passed = not failures and bool(path_a.get("roi") is not None and path_a["roi"] > 0 and confluence.get("roi") is not None and confluence["roi"] > path_a["roi"])
    return {"stage": 0, "status": "PASS" if passed else "HOLD", "config": asdict(config), "path_a": path_a, "path_b": path_b, "confluence": confluence, "devils_advocate_failures": failures, "disclaimer": "No production signal is authorized until status PASS is independently reviewed."}


def write_report(report: dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, default=str)
