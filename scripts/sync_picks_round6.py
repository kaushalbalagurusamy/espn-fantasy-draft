import pandas as pd
import json
import os

PLAYERS_FILE = 'data/players.csv'
STATE_FILE = 'data/draft_state.json'

df = pd.read_csv(PLAYERS_FILE)

# Missing players to add
new_players = [
    {
        'name': 'Tyler Warren',
        'pos': 'TE',
        'team': 'IND',
        'espn_adp': 65.0,
        'ecr': 65.0,
        'injury_risk': 'Low',
        'rush_att': 0, 'rush_yds': 0, 'rush_tds': 0,
        'targets': 75, 'rec': 55, 'rec_yds': 620, 'rec_tds': 5,
        'pass_yds': 0, 'pass_tds': 0, 'pass_int': 0, 'fumbles': 0,
        'notes': 'Collegiate star TE (Penn State) drafted in Round 5.'
    },
    {
        'name': 'Jadarian Price',
        'pos': 'RB',
        'team': 'SEA',
        'espn_adp': 70.0,
        'ecr': 70.0,
        'injury_risk': 'Low',
        'rush_att': 160, 'rush_yds': 720, 'rush_tds': 6,
        'targets': 35, 'rec': 25, 'rec_yds': 180, 'rec_tds': 1,
        'pass_yds': 0, 'pass_tds': 0, 'pass_int': 0, 'fumbles': 1,
        'notes': 'Notre Dame explosive back drafted by Seattle in Round 5.'
    },
    {
        'name': 'Bhayshul Tuten',
        'pos': 'RB',
        'team': 'JAX',
        'espn_adp': 75.0,
        'ecr': 75.0,
        'injury_risk': 'Low',
        'rush_att': 150, 'rush_yds': 680, 'rush_tds': 5,
        'targets': 30, 'rec': 20, 'rec_yds': 150, 'rec_tds': 1,
        'pass_yds': 0, 'pass_tds': 0, 'pass_int': 0, 'fumbles': 1,
        'notes': 'Virginia Tech dynamic playmaker drafted by Jacksonville.'
    },
    {
        'name': 'Jameson Williams',
        'pos': 'WR',
        'team': 'DET',
        'espn_adp': 68.0,
        'ecr': 68.0,
        'injury_risk': 'Low',
        'rush_att': 5, 'rush_yds': 40, 'rush_tds': 0,
        'targets': 80, 'rec': 52, 'rec_yds': 780, 'rec_tds': 5,
        'pass_yds': 0, 'pass_tds': 0, 'pass_int': 0, 'fumbles': 1,
        'notes': 'Electric deep-threat WR for the high-powered Lions offense.'
    },
    {
        'name': 'Jaxson Dart',
        'pos': 'QB',
        'team': 'NYG',
        'espn_adp': 80.0,
        'ecr': 80.0,
        'injury_risk': 'Low',
        'rush_att': 60, 'rush_yds': 350, 'rush_tds': 3,
        'targets': 0, 'rec': 0, 'rec_yds': 0, 'rec_tds': 0,
        'pass_yds': 3200, 'pass_tds': 20, 'pass_int': 10, 'fumbles': 3,
        'notes': 'Dual-threat Ole Miss QB rookie drafted in Round 6.'
    }
]

max_id = int(df['player_id'].max())
added_count = 0
for np in new_players:
    if not (df['name'].str.lower() == np['name'].lower()).any():
        max_id += 1
        np['player_id'] = max_id
        np['base_points'] = 150.0
        np['espn_pos_rank'] = 25
        df = pd.concat([df, pd.DataFrame([np])], ignore_index=True)
        added_count += 1
        print(f"Added new player: {np['name']} (ID {max_id})")

df.to_csv(PLAYERS_FILE, index=False)
print(f"Total players now: {len(df)}")

# Now construct the exact 72 draft picks
picks_ordered = [
    # Round 1 (1-14)
    (1, "Jahmyr Gibbs", "RB", "DET", False),
    (2, "Bijan Robinson", "RB", "ATL", False),
    (3, "Ja'Marr Chase", "WR", "CIN", False),
    (4, "Jaxon Smith-Njigba", "WR", "SEA", False),
    (5, "Amon-Ra St. Brown", "WR", "DET", False),
    (6, "Puka Nacua", "WR", "LAR", False),
    (7, "Jonathan Taylor", "RB", "IND", False),
    (8, "Christian McCaffrey", "RB", "SF", False),
    (9, "James Cook", "RB", "BUF", False),
    (10, "De'Von Achane", "RB", "MIA", False),
    (11, "CeeDee Lamb", "WR", "DAL", False),
    (12, "Justin Jefferson", "WR", "MIN", False),
    (13, "Omarion Hampton", "RB", "FA", False),
    (14, "Saquon Barkley", "RB", "PHI", True),
    
    # Round 2 (15-28)
    (15, "Breece Hall", "RB", "NYJ", True),
    (16, "Derrick Henry", "RB", "BAL", False),
    (17, "Chase Brown", "RB", "CIN", False),
    (18, "Drake London", "WR", "ATL", False),
    (19, "A.J. Brown", "WR", "PHI", False),
    (20, "Kenneth Walker III", "RB", "SEA", False),
    (21, "Josh Allen", "QB", "BUF", False),
    (22, "Nico Collins", "WR", "HOU", False),
    (23, "Trey McBride", "TE", "ARI", False),
    (24, "D'Andre Swift", "RB", "CHI", False),
    (25, "Kyren Williams", "RB", "LAR", False),
    (26, "Ashton Jeanty", "RB", "LV", False),
    (27, "Brock Bowers", "TE", "LV", False),
    (28, "George Pickens", "WR", "PIT", False),
    
    # Round 3 (29-42)
    (29, "Chris Olave", "WR", "NO", False),
    (30, "Rashee Rice", "WR", "KC", False),
    (31, "Bucky Irving", "RB", "TB", False),
    (32, "Javonte Williams", "RB", "DEN", False),
    (33, "DeVonta Smith", "WR", "PHI", False),
    (34, "Jeremiyah Love", "RB", "ARI", False),
    (35, "Garrett Wilson", "WR", "NYJ", False),
    (36, "Travis Etienne Jr.", "RB", "JAX", False),
    (37, "Malik Nabers", "WR", "NYG", False),
    (38, "Quinshon Judkins", "RB", "CLE", False),
    (39, "Tetairoa McMillan", "WR", "CAR", False),
    (40, "David Montgomery", "RB", "DET", False),
    (41, "Zay Flowers", "WR", "BAL", False),
    (42, "Travis Kelce", "TE", "KC", True),
    
    # Round 4 (43-56)
    (43, "Patrick Mahomes", "QB", "KC", True),
    (44, "Cam Skattebo", "RB", "ARI", False),
    (45, "Emeka Egbuka", "WR", "TB", False),
    (46, "Colston Loveland", "TE", "CHI", False),
    (47, "Tee Higgins", "WR", "CIN", False),
    (48, "Jaylen Waddle", "WR", "MIA", False),
    (49, "Davante Adams", "WR", "LV", False),
    (50, "Lamar Jackson", "QB", "BAL", False),
    (51, "Ladd McConkey", "WR", "LAC", False),
    (52, "George Kittle", "TE", "SF", False),
    (53, "Sam LaPorta", "TE", "DET", False),
    (54, "Kyle Pitts", "TE", "ATL", False),
    (55, "Jayden Daniels", "QB", "WAS", False),
    (56, "Joe Burrow", "QB", "CIN", False),
    
    # Round 5 (57-70)
    (57, "Tyler Warren", "TE", "IND", False),
    (58, "Drake Maye", "QB", "NE", False),
    (59, "Terry McLaurin", "WR", "WAS", False),
    (60, "Courtland Sutton", "WR", "DEN", False),
    (61, "Justin Herbert", "QB", "LAC", False),
    (62, "Jadarian Price", "RB", "SEA", False),
    (63, "Rhamondre Stevenson", "RB", "NE", False),
    (64, "DJ Moore", "WR", "CHI", False),
    (65, "Luther Burden III", "WR", "NE", False),
    (66, "Bhayshul Tuten", "RB", "JAX", False),
    (67, "TreVeyon Henderson", "RB", "DAL", False),
    (68, "Mike Evans", "WR", "TB", False),
    (69, "Jameson Williams", "WR", "DET", False),
    (70, "Isiah Pacheco", "RB", "KC", True),
    
    # Round 6 (71-72)
    (71, "Mark Andrews", "TE", "BAL", True),
    (72, "Jaxson Dart", "QB", "NYG", False)
]

from src.engine import get_processed_player_pool
processed_df, _, _ = get_processed_player_pool()

draft_history = []
drafted_ids = set()

for pick_num, name, pos, team, by_jayme in picks_ordered:
    round_num = ((pick_num - 1) // 14) + 1
    match = processed_df[processed_df['name'].str.lower() == name.lower()]
    if not match.empty:
        p_row = match.iloc[0]
        p_id = int(p_row['player_id'])
        c_ev = float(p_row['context_ev'])
        p_pos = str(p_row['pos'])
        p_team = str(p_row['team'])
    else:
        p_id = 900 + pick_num
        c_ev = 160.0
        p_pos = pos
        p_team = team
        
    drafted_ids.add(p_id)
    draft_history.append({
        'pick_num': pick_num,
        'round_num': round_num,
        'player_id': p_id,
        'player_name': name,
        'pos': p_pos,
        'team': p_team,
        'drafted_by_jayme': by_jayme,
        'context_ev': c_ev
    })

state_data = {
    'draft_history': draft_history,
    'drafted_ids': list(drafted_ids)
}

with open(STATE_FILE, 'w') as f:
    json.dump(state_data, f, indent=2)

print(f"Successfully saved {len(draft_history)} picks to {STATE_FILE}!")
print(f"Jayme's roster now has: {[p['player_name'] for p in draft_history if p['drafted_by_jayme']]}")
