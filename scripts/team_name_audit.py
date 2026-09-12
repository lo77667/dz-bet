from pathlib import Path
import pandas as pd, json, re
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def norm(x): return re.sub(r'\s+(FC|AFC)$','',str(x).strip())
fd=Counter(); of=Counter()
for p in sorted((ROOT/'data/raw/football-data-uk/E1').glob('*.csv')):
 d=pd.read_csv(p,encoding='latin-1'); fd.update(norm(x) for x in d.HomeTeam); fd.update(norm(x) for x in d.AwayTeam)
for p in sorted((ROOT/'data/raw/openfootball').glob('*-championship.json')):
 for m in json.loads(p.read_text())['matches']:
  of[norm(m['team1'])]+=1; of[norm(m['team2'])]+=1
print('football-data only names:',sorted(set(fd)-set(of)))
print('openfootball only names:',sorted(set(of)-set(fd)))
