import pandas as pd
import json
from src.state import DraftState, STATE_FILE
from src.engine import get_processed_player_pool

# 1. Add missing 2025/2026 collegiate/rookie stars to data/players.csv
df = pd.read_csv('data/players.csv')

new_stars = [
    {"name": "Ashton Jeanty", "pos": "RB", "team": "LV", "espn_adp": 26.0, "ecr": 25.0, "injury_risk": "Low",
     "rush_att": 240, "rush_yds": 1150, "rush_tds": 11, "targets": 45, "rec": 35, "rec_yds": 280, "rec_tds": 2, "pass_yds": 0, "pass_tds": 0, "pass_int": 0, "fumbles": 2, "notes": "Boise State superstar RB; drafted in Round 2."},
    {"name": "Jeremiyah Love", "pos": "RB", "team": "ARI", "espn_adp": 34.0, "ecr": 35.0, "injury_risk": "Low",
     "rush_att": 190, "rush_yds": 900, "rush_tds": 7, "targets": 40, "rec": 30, "rec_yds": 240, "rec_tds": 1, "pass_yds": 0, "pass_tds": 0, "pass_int": 0, "fumbles": 1, "notes": "Notre Dame dynamic all-purpose RB."},
    {"name": "Quinshon Judkins", "pos": "RB", "team": "CLE", "espn_adp": 38.0, "ecr": 40.0, "injury_risk": "Low",
     "rush_att": 210, "rush_yds": 980, "rush_tds": 9, "targets": 30, "rec": 22, "rec_yds": 160, "rec_tds": 1, "pass_yds": 0, "pass_tds": 0, "pass_int": 0, "fumbles": 2, "notes": "Powerhouse runner from Ohio State / Ole Miss."},
    {"name": "Tetairoa McMillan", "pos": "WR", "team": "CAR", "espn_adp": 39.0, "ecr": 38.0, "injury_risk": "Low",
     "rush_att": 0, "rush_yds": 0, "rush_tds": 0, "targets": 120, "rec": 78, "rec_yds": 1050, "rec_tds": 7, "pass_yds": 0, "pass_tds": 0, "pass_int": 0, "fumbles": 1, "notes": "6'5 physical alpha WR from Arizona."},
    {"name": "Luther Burden III", "pos": "WR", "team": "NE", "espn_adp": 45.0, "ecr": 42.0, "injury_risk": "Low",
     "rush_att": 10, "rush_yds": 80, "rush_tds": 1, "targets": 115, "rec": 80, "rec_yds": 1020, "rec_tds": 6, "pass_yds": 0, "pass_tds": 0, "pass_int": 0, "fumbles": 1, "notes": "Missouri YAC monster, Deebo-like archetype."},
    {"name": "Travis Hunter", "pos": "WR", "team": "JAX", "espn_adp": 50.0, "ecr": 45.0, "injury_risk": "Low",
     "rush_att": 5, "rush_yds": 30, "rush_tds": 0, "targets": 110, "rec": 75, "rec_yds": 980, "rec_tds": 7, "pass_yds": 0, "pass_tds": 0, "pass_int": 0, "fumbles": 1, "notes": "Two-way generational phenom from Colorado."},
    {"name": "Emeka Egbuka", "pos": "WR", "team": "TB", "espn_adp": 60.0, "ecr": 55.0, "injury_risk": "Low",
     "rush_att": 5, "rush_yds": 30, "rush_tds": 0, "targets": 95, "rec": 68, "rec_yds": 850, "rec_tds": 5, "pass_yds": 0, "pass_tds": 0, "pass_int": 0, "fumbles": 1, "notes": "Polished Ohio State slot route technician."},
    {"name": "TreVeyon Henderson", "pos": "RB", "team": "DAL", "espn_adp": 55.0, "ecr": 52.0, "injury_risk": "Medium",
     "rush_att": 170, "rush_yds": 820, "rush_tds": 7, "targets": 45, "rec": 36, "rec_yds": 300, "rec_tds": 2, "pass_yds": 0, "pass_tds": 0, "pass_int": 0, "fumbles": 2, "notes": "Explosive home-run hitting RB with high pass-catching ability."},
    {"name": "Ollie Gordon II", "pos": "RB", "team": "DEN", "espn_adp": 65.0, "ecr": 60.0, "injury_risk": "Low",
     "rush_att": 190, "rush_yds": 880, "rush_tds": 8, "targets": 30, "rec": 22, "rec_yds": 170, "rec_tds": 1, "pass_yds": 0, "pass_tds": 0, "pass_int": 0, "fumbles": 2, "notes": "Doak Walker winner workhorse back from Oklahoma State."},
    {"name": "Colston Loveland", "pos": "TE", "team": "CHI", "espn_adp": 75.0, "ecr": 70.0, "injury_risk": "Low",
     "rush_att": 0, "rush_yds": 0, "rush_tds": 0, "targets": 85, "rec": 60, "rec_yds": 720, "rec_tds": 5, "pass_yds": 0, "pass_tds": 0, "pass_int": 0, "fumbles": 1, "notes": "Michigan top TE prospect; elite separation."},
    {"name": "Cam Ward", "pos": "QB", "team": "TEN", "espn_adp": 120.0, "ecr": 115.0, "injury_risk": "Low",
     "rush_att": 50, "rush_yds": 220, "rush_tds": 2, "targets": 0, "rec": 0, "rec_yds": 0, "rec_tds": 0, "pass_yds": 3600, "pass_tds": 23, "pass_int": 11, "fumbles": 3, "notes": "Miami Hurricanes playmaking QB."},
    {"name": "Shedeur Sanders", "pos": "QB", "team": "LV", "espn_adp": 125.0, "ecr": 118.0, "injury_risk": "Low",
     "rush_att": 40, "rush_yds": 120, "rush_tds": 2, "targets": 0, "rec": 0, "rec_yds": 0, "rec_tds": 0, "pass_yds": 3700, "pass_tds": 24, "pass_int": 10, "fumbles": 3, "notes": "Pinpoint pocket accuracy from Colorado."}
]

max_id = df['player_id'].max()
rows_to_add = []
for s in new_stars:
    if not (df['name'].str.lower() == s['name'].lower()).any():
        max_id += 1
        s['player_id'] = max_id
        s['base_points'] = 200.0
        rows_to_add.append(s)

if rows_to_add:
    df = pd.concat([df, pd.DataFrame(rows_to_add)], ignore_index=True)
    df.to_csv('data/players.csv', index=False)
    print(f"Added {len(rows_to_add)} rookie/college stars to data/players.csv")

# 2. Reload processed player pool
all_players_df, baselines, cfg = get_processed_player_pool()

# 3. Complete verified 43 picks in exact draft order:
all_picks = [
    # Round 1 (Picks 1-14)
    ("Jahmyr Gibbs", False),          # 1.1 (Pick 1)
    ("Bijan Robinson", False),        # 1.2 (Pick 2)
    ("Ja'Marr Chase", False),         # 1.3 (Pick 3)
    ("Jaxon Smith-Njigba", False),    # 1.4 (Pick 4)
    ("Amon-Ra St. Brown", False),     # 1.5 (Pick 5)
    ("Puka Nacua", False),            # 1.6 (Pick 6)
    ("Jonathan Taylor", False),       # 1.7 (Pick 7)
    ("Christian McCaffrey", False),   # 1.8 (Pick 8)
    ("James Cook", False),            # 1.9 (Pick 9)
    ("De'Von Achane", False),         # 1.10 (Pick 10)
    ("CeeDee Lamb", False),           # 1.11 (Pick 11)
    ("Justin Jefferson", False),      # 1.12 (Pick 12)
    ("Omarion Hampton", False),       # 1.13 (Pick 13)
    ("Saquon Barkley", True),         # 1.14 (Pick 14) -> JAYME!

    # Round 2 (Picks 15-28)
    ("Breece Hall", True),            # 2.1 (Pick 15) -> JAYME!
    ("Derrick Henry", False),         # 2.2 (Pick 16)
    ("Chase Brown", False),           # 2.3 (Pick 17)
    ("Drake London", False),          # 2.4 (Pick 18)
    ("A.J. Brown", False),            # 2.5 (Pick 19)
    ("Kenneth Walker III", False),    # 2.6 (Pick 20)
    ("Josh Allen", False),            # 2.7 (Pick 21)
    ("Nico Collins", False),          # 2.8 (Pick 22)
    ("Trey McBride", False),          # 2.9 (Pick 23)
    ("D'Andre Swift", False),         # 2.10 (Pick 24)
    ("Kyren Williams", False),        # 2.11 (Pick 25)
    ("Ashton Jeanty", False),         # 2.12 (Pick 26)
    ("Brock Bowers", False),          # 2.13 (Pick 27)
    ("George Pickens", False),        # 2.14 (Pick 28)

    # Round 3 (Picks 29-42)
    ("Chris Olave", False),           # 3.1 (Pick 29)
    ("Rashee Rice", False),           # 3.2 (Pick 30)
    ("Bucky Irving", False),          # 3.3 (Pick 31)
    ("Javonte Williams", False),      # 3.4 (Pick 32)
    ("DeVonta Smith", False),         # 3.5 (Pick 33)
    ("Jeremiyah Love", False),        # 3.6 (Pick 34)
    ("Garrett Wilson", False),        # 3.7 (Pick 35)
    ("Travis Etienne Jr.", False),    # 3.8 (Pick 36)
    ("Malik Nabers", False),          # 3.9 (Pick 37)
    ("Quinshon Judkins", False),      # 3.10 (Pick 38)
    ("Tetairoa McMillan", False),     # 3.11 (Pick 39)
    ("David Montgomery", False),      # 3.12 (Pick 40)
    ("Zay Flowers", False),           # 3.13 (Pick 41)
    ("Travis Kelce", True),           # 3.14 (Pick 42) -> JAYME!

    # Round 4 (Picks 43...)
    ("Patrick Mahomes", True),        # 4.1 (Pick 43) -> JAYME!
]

state = DraftState()
state.draft_history = []
state.drafted_ids = set()
state.roster_manager.drafted_players = []

for name, for_jayme in all_picks:
    matched = state.all_players_df[state.all_players_df['name'].str.lower() == name.lower()]
    if not matched.empty:
        p_id = matched.iloc[0]['player_id']
        state.draft_player(p_id, for_jayme=for_jayme)
    else:
        print(f"Warning: could not find {name}, adding as custom")
        state.draft_custom_player(name, pos="RB", for_jayme=for_jayme)

state.save_to_disk()
print(f"\n========================================================")
print(f"Successfully initialized ALL {len(state.draft_history)} picks into draft_state.json!")
print(f"Current Pick: #{state.current_pick} (Round {state.current_round})")
print(f"Picks until Jayme's next turn: {state.picks_until_next_turn} picks away (Picks 70 & 71)")
print("========================================================\n")

print("Jayme's Roster (4 Rounds Complete):")
for s, p in state.roster_manager.get_slot_allocations().items():
    if p:
        print(f"  {s}: {p['name']} ({p['pos']} - {p['team']}) - {p['context_ev']:.1f} EV")
    else:
        print(f"  {s}: [OPEN]")

avail = state.get_available_players_df()
print("\nTop 10 Targets for Jayme's Round 5 & 6 Turn (Picks 70 & 71):")
print(avail[['name', 'pos', 'team', 'context_ev', 'marginal_ev', 'role_addition', 'espn_value_delta']].head(10).to_string(index=False))
