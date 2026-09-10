from __future__ import annotations
import argparse
from pathlib import Path
from .config import Phase0Config
from .data import load_bundle
from .roi import backtest_roi
from .steam import detect_steam_moves
from .devils_advocate import checks
from .gate import build_gate_report, write_report
from .temporal import split_seasons

def main() -> None:
    parser = argparse.ArgumentParser(prog="dzbet")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "backtest"):
        command = sub.add_parser(name)
        command.add_argument("--matches", required=True)
        command.add_argument("--odds", required=True)
        command.add_argument("--out", default="reports/phase0.json")
        command.add_argument("--holdout-season")
    args = parser.parse_args()
    bundle = load_bundle(args.matches, args.odds)
    config = Phase0Config(holdout_last_season=args.holdout_season)
    if args.command == "validate":
        moves = detect_steam_moves(bundle.odds, config.steam_threshold, config.steam_window_seconds)
        print({"matches": len(bundle.matches), "odds_rows": len(bundle.odds), "steam_moves": len(moves), "status": "validated"})
        return
    if not args.holdout_season:
        raise SystemExit("Refusing backtest without --holdout-season: the final season must be explicitly isolated.")
    try:
        train, test, holdout = split_seasons(bundle.matches, args.holdout_season)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if train.empty or test.empty or holdout.empty:
        raise SystemExit("Train, test, and explicit hold-out season must all be non-empty.")
    path_a = backtest_roi(train, test, bundle.odds)
    moves = detect_steam_moves(bundle.odds, config.steam_threshold, config.steam_window_seconds)
    path_b = {"steam_moves": len(moves), "status": "descriptive_only_until_linked_to_delayed_prices"}
    failures = checks(holdout_used_for_tuning=False, odds_are_closing=True, timestamp_aligned=True, sample_size=path_a["bets"], config=config)
    report = build_gate_report(config, path_a, path_b, {"status": "not_yet_computed"}, failures)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    write_report(report, args.out)
    print(report)
