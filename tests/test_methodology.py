import pandas as pd
import pytest
from dzbet.benchmarks import base_rate_probabilities
from dzbet.poisson import fit_poisson
from dzbet.temporal import split_seasons, validate_season_boundaries


def season_rows():
    rows = []
    for season, year in [("2021-2022", 2021), ("2022-2023", 2022), ("2023-2024", 2023), ("2024-2025", 2024)]:
        rows.append({"match_id": season, "date": pd.Timestamp(f"{year}-08-01", tz="UTC"), "home_team":"A", "away_team":"B", "home_goals":1, "away_goals":0, "season":season})
    return pd.DataFrame(rows)


def test_season_boundaries_do_not_overlap():
    matches = season_rows()
    validate_season_boundaries(matches)
    with pytest.raises(ValueError, match="outside declared season"):
        invalid = matches.copy()
        invalid.loc[0, "date"] = pd.Timestamp("2022-07-01", tz="UTC")
        validate_season_boundaries(invalid)


def test_holdout_season_not_in_train():
    train, test, holdout = split_seasons(season_rows(), "2024-2025")
    assert "2024-2025" not in set(train.season)
    assert "2024-2025" not in set(test.season)
    assert set(holdout.season) == {"2024-2025"}


def test_split_requires_two_training_seasons():
    with pytest.raises(ValueError, match="at least two seasons"):
        split_seasons(season_rows().iloc[-2:], "2024-2025")


def test_poisson_beats_base_rate_on_simple_out_of_sample_case():
    train = pd.DataFrame([
        {"home_team":"A","away_team":"B","home_goals":3,"away_goals":0},
        {"home_team":"A","away_team":"B","home_goals":3,"away_goals":0},
        {"home_team":"B","away_team":"A","home_goals":0,"away_goals":2},
        {"home_team":"B","away_team":"A","home_goals":0,"away_goals":2},
    ])
    model = fit_poisson(train)
    assert model.probabilities("A", "B")["home"] > base_rate_probabilities(train)["home"]
