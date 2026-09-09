import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "league_rules.yaml")

def load_league_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def get_jayme_pick_numbers(teams_count=14, rounds=15, slot=14):
    """
    Returns the list of overall pick numbers for Jayme's slot in a snake draft.
    For slot 14 in 14-team snake:
    Round 1: pick 14
    Round 2: pick 15
    Round 3: pick 42
    Round 4: pick 43
    ...
    """
    picks = []
    for r in range(1, rounds + 1):
        if r % 2 == 1:  # Odd round: 1, 2, ..., 14
            p = (r - 1) * teams_count + slot
        else:           # Even round: 14, 13, ..., 1 -> slot 14 is 1st pick of round
            p = (r - 1) * teams_count + (teams_count - slot + 1)
        picks.append(p)
    return sorted(picks)
