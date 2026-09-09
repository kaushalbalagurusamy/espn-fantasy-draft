import json
import pandas as pd
from src.state import DraftState, STATE_FILE

# Ordered list of picks made so far:
picks_order = [
    # Round 1
    (11, False),   # 1.1: Jahmyr Gibbs
    (7, False),    # 1.2: Bijan Robinson
    (4, False),    # 1.3: Ja'Marr Chase
    (85, False),   # 1.4: Jaxon Smith-Njigba
    (6, False),    # 1.5: Amon-Ra St. Brown
    (14, False),   # 1.6: Puka Nacua
    (13, False),   # 1.7: Jonathan Taylor
    (1, False),    # 1.8: Christian McCaffrey
    (47, False),   # 1.9: James Cook
    (21, False),   # 1.10: De'Von Achane
    (2, False),    # 1.11: CeeDee Lamb
    (5, False),    # 1.12: Justin Jefferson
    (238, False),  # 1.13: Omarion Hampton
    (12, True),    # 1.14: Saquon Barkley (JAYME)

    # Round 2
    (8, True),     # 2.1 (15): Breece Hall (JAYME)
    (18, False),   # 2.2 (16): Derrick Henry
    (97, False),   # 2.3 (17): Chase Brown
    (17, False),   # 2.4 (18): Drake London
    (9, False),    # 2.5 (19): A.J. Brown
    (49, False),   # 2.6 (20): Kenneth Walker III
    (29, False),   # 2.7 (21): Josh Allen
    (22, False),   # 2.8 (22): Nico Collins
    (26, False),   # 2.9 (23): Trey McBride
    (54, False),   # 2.10 (24): D'Andre Swift
]

state = DraftState()
# Clear and rebuild
state.draft_history = []
state.drafted_ids = set()
state.roster_manager.drafted_players = []

for p_id, for_jayme in picks_order:
    state.draft_player(p_id, for_jayme=for_jayme)

state.save_to_disk()
print(f"Successfully initialized draft_state.json with {len(state.draft_history)} picks.")
print(f"Current pick: #{state.current_pick}, Round: {state.current_round}")
print(f"Picks until Jayme's next turn: {state.picks_until_next_turn} (at Pick #{state.current_pick + state.picks_until_next_turn})")
print("\nJayme's Current Roster:")
for s, p in state.roster_manager.get_slot_allocations().items():
    if p:
        print(f"  {s}: {p['name']} ({p['pos']} - {p['team']}) - {p['context_ev']:.1f} pts")
    else:
        print(f"  {s}: [OPEN]")

avail = state.get_available_players_df()
print("\nTop 10 Recommendations for Jayme's Next Target (Picks 42 & 43):")
print(avail[['name', 'pos', 'team', 'context_ev', 'marginal_ev', 'role_addition', 'espn_value_delta']].head(10).to_string(index=False))
