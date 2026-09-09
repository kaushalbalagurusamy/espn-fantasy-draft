import pandas as pd

df = pd.read_csv('data/players.csv')

# 1. Zero out Tyreek Hill
hill_mask = df['name'].str.lower() == 'tyreek hill'
if hill_mask.any():
    df.loc[hill_mask, 'injury_risk'] = 'OUT'
    df.loc[hill_mask, 'notes'] = 'OUT - Severe knee injury, unsigned FA. Do not draft.'
    df.loc[hill_mask, 'base_points'] = 0.0
    df.loc[hill_mask, 'rec'] = 0
    df.loc[hill_mask, 'rec_yds'] = 0
    df.loc[hill_mask, 'rec_tds'] = 0

# 2. Tag other notable PUP / IR players
pup_players = {
    'T.J. Hockenson': 'Starting on PUP (recovering from ACL); late-season stash only.',
    'Nick Chubb': 'Starting on PUP (recovering from multi-ligament knee); mid-season return.',
    'Jonathon Brooks': 'Starting on PUP (recovering from ACL); second-half rookie upside.',
    'Hollywood Brown': 'Starting on IR (sternoclavicular shoulder injury); out first 4-8 weeks.'
}

for name, note in pup_players.items():
    mask = df['name'].str.lower() == name.lower()
    if mask.any():
        df.loc[mask, 'injury_risk'] = 'PUP/IR'
        df.loc[mask, 'notes'] = note

df.to_csv('data/players.csv', index=False)
print("Updated player injuries in data/players.csv successfully!")
