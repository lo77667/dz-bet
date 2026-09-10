from __future__ import annotations

import argparse
from pathlib import Path
from .data import load_bundle
from .baseline import backtest_baseline
from .gate import GateConfig, build_gate_report, devil_advocate_checks, write_report
from .signals import detect_steam_moves


def main() -> None:
    parser = argparse.ArgumentParser(prog="dzbet")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "backtest"):
        p = sub.add_parser(name)
        p.add_argument("--matches", required=True)
        p.add_argument("--odds", required=True)
        p.add_argument("--out", default="reports/phase0.json")
        p.add_argument("--holdout-season")
    args = parser.parse_args()
    bundle = load_bundle(args.matches, args.odds)
    if args.command == "validate":
        moves = detect_steam_moves(bundle.odds)
        print({"matches": len(bundle.matches), "odds_rows": len(bundle.odds), "steam_moves": len(moves), "status": "validated"})
        return
    if not args.holdout_season:
        raise SystemExit("Refusing backtest without --holdout-season: the final season must be explicitly isolated.")
    train = bundle.matches[bundle.matches.season != args.holdout_season]
    test = bundle.matches[bundle.matches.season == args.holdout_season]
    if train.empty or test.empty:
        raise SystemExit("Both training data and the explicit hold-out season must be non-empty.")
    path_a = backtest_baseline(train, test, bundle.odds)
    moves = detect_steam_moves(bundle.odds)
    path_b = {"steam_moves": len(moves), "status": "descriptive_only_until_linked_to_delayed_prices"}
    failures = devil_advocate_checks(holdout_used_for_tuning=False, odds_are_closing=True, timestamp_aligned=True, sample_size=path_a["bets"], config=GateConfig(holdout_last_season=args.holdout_season))
    report = build_gate_report(GateConfig(holdout_last_season=args.holdout_season), path_a, path_b, {"status": "not_yet_computed"}, failures)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    write_report(report, args.out)
    print(report)
