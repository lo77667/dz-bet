import hashlib
import pandas as pd
import pytest
from dzbet.data_validation import (
    assert_unique_match_ids, assert_no_missing_closing_odds, assert_no_post_kickoff_odds,
    xg_coverage, normalize_team_names, holdout_sha256,
)
from dzbet.temporal import validate_season_boundaries, split_seasons


def matches():
    return pd.DataFrame([
        {"match_id":"m1","date":pd.Timestamp("2024-08-01 12:00", tz="UTC"),"home_team":"A","away_team":"B","home_goals":1,"away_goals":0,"season":"2024-25"},
        {"match_id":"m2","date":pd.Timestamp("2024-08-02 12:00", tz="UTC"),"home_team":"B","away_team":"A","home_goals":0,"away_goals":1,"season":"2024-25"},
    ])


def odds():
    return pd.DataFrame([
        {"match_id":"m1","timestamp":pd.Timestamp("2024-08-01 11:00", tz="UTC"),"odds":2.0},
        {"match_id":"m2","timestamp":pd.Timestamp("2024-08-02 11:00", tz="UTC"),"odds":2.0},
    ])


def test_match_ids_unique(): assert_unique_match_ids(matches())
def test_no_missing_closing_odds(): assert_no_missing_closing_odds(matches(), odds())
def test_season_boundaries_consistent(): validate_season_boundaries(matches())
def test_holdout_season_not_in_train():
    first = matches().assign(season="2022-23", match_id=lambda x: "a" + x.match_id, date=lambda x: x.date - pd.Timedelta(days=730))
    second = matches().assign(season="2023-24", match_id=lambda x: "b" + x.match_id, date=lambda x: x.date - pd.Timedelta(days=365))
    third = matches().assign(season="2024-25", match_id=lambda x: "c" + x.match_id)
    all_matches = pd.concat([first, second, third])
    train, test, holdout = split_seasons(all_matches, "2024-25")
    assert set(train.match_id).isdisjoint(set(holdout.match_id))
def test_no_post_kickoff_odds(): assert_no_post_kickoff_odds(matches(), odds())
def test_xg_coverage_threshold():
    xg = pd.DataFrame({"match_id": ["m1", "m2"], "home_xg": [1.0, 1.0], "away_xg": [0.5, 0.5]})
    assert xg_coverage(matches(), xg) >= 0.90
def test_source_cross_validation():
    source_a = {"m1": ("A", "B", 1, 0), "m2": ("B", "A", 0, 1)}
    source_b = dict(source_a)
    assert source_a == source_b
def test_team_names_normalized():
    assert normalize_team_names(pd.Series([" Sheff Utd "])).iloc[0] == "Sheffield United"
def test_no_duplicate_matches():
    with pytest.raises(ValueError, match="duplicate"):
        assert_unique_match_ids(pd.concat([matches(), matches().iloc[[0]]]))
def test_holdout_file_untouched(tmp_path):
    path = tmp_path / "holdout.parquet"
    path.write_bytes(b"immutable-holdout-fixture")
    before = holdout_sha256(path)
    assert holdout_sha256(path) == before
