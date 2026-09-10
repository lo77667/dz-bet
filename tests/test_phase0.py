import pandas as pd
import pytest
from dzbet.data import load_matches, load_odds
from dzbet.signals import detect_steam_moves, confluence_decision, team_stability_score
from dzbet.gate import GateConfig, devil_advocate_checks


def test_rejects_invalid_odds(tmp_path):
    p = tmp_path / "odds.csv"
    pd.DataFrame([{"match_id": "m1", "bookmaker": "x", "market": "1X2", "selection": "home", "odds": 1.0, "timestamp": "2024-01-01T00:00:00Z"}]).to_csv(p, index=False)
    with pytest.raises(ValueError, match="greater than 1"):
        load_odds(p)


def test_steam_move_is_timestamp_bounded():
    df = pd.DataFrame([
        {"match_id":"m1","bookmaker":"sharp","market":"1X2","selection":"home","odds":2.0,"timestamp":"2024-01-01T00:00:00Z"},
        {"match_id":"m1","bookmaker":"sharp","market":"1X2","selection":"home","odds":2.12,"timestamp":"2024-01-01T00:02:00Z"},
    ])
    df["timestamp"] = pd.to_datetime(df.timestamp, utc=True)
    assert len(detect_steam_moves(df)) == 1


def test_confluence_matrix():
    assert confluence_decision(True, True) == "priority"
    assert confluence_decision(True, False) == "caution"
    assert confluence_decision(False, True) == "monitor"
    assert confluence_decision(False, False) == "ignore"


def test_stability_score_weights_unofficial_sources():
    df = pd.DataFrame([{"team":"A","timestamp":"2024-01-01T00:00:00Z","text":"injury doubt","source_type":"journalist"}])
    result = team_stability_score(df)
    assert result.iloc[0].weighted_negative == 2.0
    assert result.iloc[0].team_stability_score < 1.0


def test_gate_rejects_small_sample_and_unproven_assumptions():
    failures = devil_advocate_checks(holdout_used_for_tuning=False, odds_are_closing=False, timestamp_aligned=True, sample_size=2, config=GateConfig(min_bets=100))
    assert len(failures) == 2
