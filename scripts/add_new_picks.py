import pandas as pd
import json
from src.state import DraftState, STATE_FILE
from src.engine import get_processed_player_pool

# 1. Check / Add Cam Skattebo
df = pd.read_csv('data/players.csv')
if not (df['name'].str.lower() == 'cam skattebo').any():
    max_id = int(df['player_id'].max()) + 1
    new_p = {
        'name': 'Cam Skattebo', 'pos': 'RB', 'team': 'ARI', 'espn_adp': 50.0, 'ecr': 48.0, 'injury_risk': 'Low',
        'rush_att': 210, 'rush_yds': 980, 'rush_tds': 9, 'targets': 35, 'rec': 28, 'rec_yds': 240, 'rec_tds': 2,
        'pass_yds': 0, 'pass_tds': 0, 'pass_int': 0, 'fumbles': 2,
        'notes': 'Arizona State powerhouse bowling ball RB.',
        'player_id': max_id, 'base_points': 215.0
    }
    df = pd.concat([df, pd.DataFrame([new_p])], ignore_index=True)
    df.to_csv('data/players.csv', index=False)
    print(f"Added Cam Skattebo to data/players.csv (ID {max_id})")

# 2. Reload state from disk
state = DraftState()
state.load_from_disk()
state.reload_player_pool()

new_drafted_names = [
    "Cam Skattebo",
    "Emeka Egbuka",
    "Colston Loveland",
    "Tee Higgins",
    "Jaylen Waddle",
    "Davante Adams",
    "Lamar Jackson",
    "Ladd McConkey",
    "George Kittle"
]

for name in new_drafted_names:
    matched = state.all_players_df[state.all_players_df['name'].str.lower() == name.lower()]
    if not matched.empty:
        p_id = int(matched.iloc[0]['player_id'])
        if p_id not in state.drafted_ids:
            state.draft_player(p_id, for_jayme=False)
            print(f"Drafted #{state.current_pick - 1}: {name} ({matched.iloc[0]['pos']})")
    else:
        print(f"Drafting custom player: {name}")
        state.draft_custom_player(name, pos="WR", for_jayme=False)

state.save_to_disk()
print(f"\n========================================================")
print(f"Total Picks Completed: {len(state.draft_history)}")
print(f"Current Pick on Clock: #{state.current_pick} (Round {state.current_round})")
print(f"Picks until Jayme's next turn: {state.picks_until_next_turn} picks away (Picks #70 & #71)")
print("========================================================\n")

avail = state.get_available_players_df()
print("Top 10 Remaining Targets for Jayme's Turn at Picks #70 & #71 (Prioritizing WRs):")
print(avail[['name', 'pos', 'team', 'context_ev', 'marginal_ev', 'role_addition', 'espn_value_delta']].head(10).to_string(index=False))
