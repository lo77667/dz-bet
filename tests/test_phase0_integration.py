import pandas as pd
from dzbet.poisson import fit_poisson
from dzbet.roi import closing_odds_before_kickoff
from dzbet.steam import detect_steam_moves


def test_poisson_probabilities_sum_to_one():
    matches = pd.DataFrame([
        {"home_team":"A","away_team":"B","home_goals":1,"away_goals":0},
        {"home_team":"B","away_team":"A","home_goals":0,"away_goals":1},
        {"home_team":"A","away_team":"B","home_goals":2,"away_goals":1},
        {"home_team":"B","away_team":"A","home_goals":1,"away_goals":1},
    ])
    probabilities = fit_poisson(matches).probabilities("A", "B")
    assert abs(sum(probabilities.values()) - 1.0) < 1e-12


def test_post_kickoff_quotes_are_excluded():
    matches = pd.DataFrame([{"match_id":"m1", "date":pd.Timestamp("2024-01-01T12:00:00Z")}])
    odds = pd.DataFrame([
        {"match_id":"m1","market":"1X2","selection":"home","bookmaker":"x","odds":2.0,"timestamp":pd.Timestamp("2024-01-01T11:59:00Z")},
        {"match_id":"m1","market":"1X2","selection":"home","bookmaker":"x","odds":9.0,"timestamp":pd.Timestamp("2024-01-01T12:01:00Z")},
    ])
    result = closing_odds_before_kickoff(matches, odds)
    assert len(result) == 1
    assert result.iloc[0].odds == 2.0


def test_steam_move_ignores_negative_time_order():
    odds = pd.DataFrame([
        {"match_id":"m1","bookmaker":"x","market":"1X2","selection":"home","odds":2.0,"timestamp":pd.Timestamp("2024-01-01T00:02:00Z")},
        {"match_id":"m1","bookmaker":"x","market":"1X2","selection":"home","odds":2.2,"timestamp":pd.Timestamp("2024-01-01T00:00:00Z")},
    ])
    assert len(detect_steam_moves(odds)) == 1
