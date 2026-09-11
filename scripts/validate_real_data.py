from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
seasons=['2019-20','2020-21','2021-22','2022-23','2023-24','2024-25','2025-26']
rows=[]
for season in seasons:
    frame=pd.read_parquet(ROOT/'data/interim/matches.parquet')
    part=frame[frame.season==season]
    assert len(part)==552, (season,len(part))
    assert not part.match_id.duplicated().any()
    rows.append((season,len(part)))
odds=pd.read_parquet(ROOT/'data/interim/odds.parquet')
assert len(odds)==len(seasons)*552*3
assert odds.odds.notna().all()
assert not (ROOT/'data/processed/holdout.parquet').exists()
print('validated seasons:', rows)
print('validated odds rows:', len(odds))
print('holdout: absent and protected')
