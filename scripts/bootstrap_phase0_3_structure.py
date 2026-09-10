from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "data/interim/matches.parquet": ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "season"],
    "data/interim/odds.parquet": ["match_id", "bookmaker", "market", "selection", "odds", "timestamp"],
    "data/interim/xg.parquet": ["match_id", "home_xg", "away_xg", "source"],
    "data/processed/train.parquet": ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "season"],
    "data/processed/test.parquet": ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "season"],
    "data/processed/holdout.parquet": ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "season"],
}
for relative, columns in SCHEMAS.items():
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        pd.DataFrame({column: pd.Series(dtype="object") for column in columns}).to_parquet(path, index=False)
        print(f"created empty schema: {relative}")
