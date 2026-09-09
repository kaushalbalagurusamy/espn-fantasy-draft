import pandas as pd
import numpy as np

class RosterManager:
    def __init__(self, config, baselines):
        self.config = config
        self.baselines = baselines
        self.roster_limits = config.get('position_limits', {
            'QB': 4, 'RB': 8, 'WR': 8, 'TE': 3, 'DST': 3, 'K': 3
        })
        self.drafted_players = []  # List of dicts representing Jayme's players

    def add_player(self, player_row):
        """Adds a player to Jayme's team."""
        player_dict = player_row.to_dict() if hasattr(player_row, 'to_dict') else dict(player_row)
        self.drafted_players.append(player_dict)

    def remove_player(self, player_name):
        """Removes a player from Jayme's team (undo action)."""
        self.drafted_players = [p for p in self.drafted_players if p['name'] != player_name]

    def get_roster_dataframe(self):
        if not self.drafted_players:
            return pd.DataFrame()
        return pd.DataFrame(self.drafted_players)

    def get_slot_allocations(self):
        """
        Optimally maps Jayme's drafted players into starting slots:
        1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX (RB/WR/TE), 1 DST, 1 K, and up to 7 Bench.
        """
        slots = {
            'QB': None,
            'RB1': None,
            'RB2': None,
            'WR1': None,
            'WR2': None,
            'TE': None,
            'FLEX': None,
            'DST': None,
            'K': None,
            'BENCH': []
        }
        
        if not self.drafted_players:
            return slots

        # Sort drafted players by context_ev descending
        sorted_players = sorted(self.drafted_players, key=lambda x: x.get('context_ev', 0), reverse=True)
        
        assigned_ids = set()

        # 1. Primary Starter Positions
        for pos, slot_names in [('QB', ['QB']), ('TE', ['TE']), ('DST', ['DST']), ('K', ['K'])]:
            candidates = [p for p in sorted_players if p['pos'] == pos and p['player_id'] not in assigned_ids]
            if candidates:
                slots[slot_names[0]] = candidates[0]
                assigned_ids.add(candidates[0]['player_id'])

        # RBs
        rb_candidates = [p for p in sorted_players if p['pos'] == 'RB' and p['player_id'] not in assigned_ids]
        if len(rb_candidates) >= 1:
            slots['RB1'] = rb_candidates[0]
            assigned_ids.add(rb_candidates[0]['player_id'])
        if len(rb_candidates) >= 2:
            slots['RB2'] = rb_candidates[1]
            assigned_ids.add(rb_candidates[1]['player_id'])

        # WRs
        wr_candidates = [p for p in sorted_players if p['pos'] == 'WR' and p['player_id'] not in assigned_ids]
        if len(wr_candidates) >= 1:
            slots['WR1'] = wr_candidates[0]
            assigned_ids.add(wr_candidates[0]['player_id'])
        if len(wr_candidates) >= 2:
            slots['WR2'] = wr_candidates[1]
            assigned_ids.add(wr_candidates[1]['player_id'])

        # FLEX (Best remaining RB, WR, or TE)
        flex_candidates = [p for p in sorted_players if p['pos'] in ['RB', 'WR', 'TE'] and p['player_id'] not in assigned_ids]
        if flex_candidates:
            slots['FLEX'] = flex_candidates[0]
            assigned_ids.add(flex_candidates[0]['player_id'])

        # Remaining go to BENCH
        for p in sorted_players:
            if p['player_id'] not in assigned_ids:
                slots['BENCH'].append(p)

        return slots

    def calculate_marginal_ev_addition(self, player, picks_until_next_turn=0):
        """
        Calculates the real role-adjusted Marginal EV addition to Jayme's team.
        Takes into account:
        - Whether player fills an empty starter hole
        - Whether player competes for FLEX
        - Diminishing returns of bench backups (especially 2nd QB or 2nd TE)
        - Positional limits
        - Pick gap urgency (26 picks between turns in snake draft at slot 14)
        """
        pos = player['pos']
        ev = player['context_ev']
        baseline = self.baselines.get(pos, 100.0)
        
        # Check injury status & 0 EV
        inj = str(player.get('injury_risk', '')).upper()
        if inj == 'OUT' or ev <= 0.0:
            return -999.0, "Inactive / OUT (Do Not Draft)"
            
        if inj in ['IR', 'INJURED RESERVE']:
            return -50.0, "⚠️ On Injured Reserve (Stash Only)"

        # Check positional limit
        current_pos_count = sum(1 for p in self.drafted_players if p['pos'] == pos)
        if current_pos_count >= self.roster_limits.get(pos, 8):
            return -999.0, "Position Limit Reached"

        slots = self.get_slot_allocations()

        # Positional starting requirements
        open_starters = {
            'QB': slots['QB'] is None,
            'RB': (slots['RB1'] is None) or (slots['RB2'] is None),
            'WR': (slots['WR1'] is None) or (slots['WR2'] is None),
            'TE': slots['TE'] is None,
            'FLEX': slots['FLEX'] is None and pos in ['RB', 'WR', 'TE'],
            'DST': slots['DST'] is None,
            'K': slots['K'] is None
        }

        # Case 1: Fills an unfilled primary starter slot
        if pos in ['QB', 'TE', 'DST', 'K'] and open_starters[pos]:
            marginal_val = ev - baseline
            role_desc = f"New Starting {pos}"
            urgency_bonus = 1.25  # High priority to secure starting lineup
            
        elif pos == 'RB' and (slots['RB1'] is None or slots['RB2'] is None):
            marginal_val = ev - baseline
            which = "RB1" if slots['RB1'] is None else "RB2"
            role_desc = f"New Starting {which}"
            urgency_bonus = 1.30  # RBs are hyper-scarce in 14-team leagues

        elif pos == 'WR' and (slots['WR1'] is None or slots['WR2'] is None):
            marginal_val = ev - baseline
            which = "WR1" if slots['WR1'] is None else "WR2"
            role_desc = f"New Starting {which}"
            urgency_bonus = 1.25  # Full PPR rewards WR target volume

        # Case 2: Primary starters filled, but FLEX is open
        elif pos in ['RB', 'WR', 'TE'] and slots['FLEX'] is None:
            marginal_val = ev - self.baselines.get('RB', 144.0) * 0.95
            role_desc = f"Starting FLEX ({pos})"
            urgency_bonus = 1.15

        # Case 3: Starters and FLEX are filled, player is BENCH
        else:
            if pos == 'QB':
                # 2nd QB in 1-QB league has very low starting utility (only week of bye or injury)
                marginal_val = (ev - baseline) * 0.20
                role_desc = "Backup QB (Bye / Insurance)"
                urgency_bonus = 0.50

            elif pos == 'TE':
                # 2nd TE also low starting utility unless elite stash
                marginal_val = (ev - baseline) * 0.25
                role_desc = "Backup TE (Depth)"
                urgency_bonus = 0.55

            elif pos in ['DST', 'K']:
                # Zero reason to draft backup K or DST
                marginal_val = -50.0
                role_desc = "Redundant K/DST (Do Not Draft)"
                urgency_bonus = 0.1

            elif pos == 'RB':
                # Backup RBs in 14-team league have ENORMOUS contingent upside / handcuff value
                marginal_val = (ev - baseline) * 0.65 + 15.0
                role_desc = "High-Upside Bench RB (Critical Depth)"
                urgency_bonus = 1.05

            elif pos == 'WR':
                # Backup WRs provide frequent bye/flex rotation
                marginal_val = (ev - baseline) * 0.60 + 10.0
                role_desc = "Bench WR (Flex Rotation)"
                urgency_bonus = 1.00

        # Turn cliff urgency adjustment:
        # If Jayme has 26 picks until next turn, missing out on an unfilled RB/WR/TE starter is fatal!
        if picks_until_next_turn >= 20 and open_starters.get(pos, False):
            urgency_bonus += 0.15

        final_marginal_ev = round(marginal_val * urgency_bonus, 1)
        return final_marginal_ev, role_desc
