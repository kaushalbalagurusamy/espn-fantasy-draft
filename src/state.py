import pandas as pd
import json
import os
from .config import load_league_config, get_jayme_pick_numbers
from .engine import get_processed_player_pool
from .roster import RosterManager

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "draft_state.json")

class DraftState:
    def __init__(self):
        self.config = load_league_config()
        self.teams_count = self.config.get('teams_count', 14)
        self.jayme_slot = self.config.get('draft_position', 14)
        
        draftable_slots = {k: v for k, v in self.config['roster_slots'].items() if k != 'IR'}
        self.total_rounds = sum(draftable_slots.values())               # 16 rounds
        self.total_picks = self.teams_count * self.total_rounds         # 224 picks
        
        self.jayme_picks = get_jayme_pick_numbers(self.teams_count, self.total_rounds, self.jayme_slot)
        
        self.all_players_df, self.baselines, _ = get_processed_player_pool()
        self.roster_manager = RosterManager(self.config, self.baselines)
        
        self.drafted_ids = set()
        self.draft_history = []
        
        # Load persisted state from disk if exists
        self.load_from_disk()

    def reload_player_pool(self):
        """Reloads player pool from players.csv while keeping all draft history intact."""
        self.all_players_df, self.baselines, _ = get_processed_player_pool()
        # Re-sync roster manager baselines
        self.roster_manager.baselines = self.baselines

    def save_to_disk(self):
        try:
            cleaned_history = []
            for h in self.draft_history:
                cleaned_history.append({
                    'pick_num': int(h['pick_num']),
                    'round_num': int(h['round_num']),
                    'player_id': int(h['player_id']),
                    'player_name': str(h['player_name']),
                    'pos': str(h['pos']),
                    'team': str(h['team']),
                    'drafted_by_jayme': bool(h['drafted_by_jayme']),
                    'context_ev': float(h['context_ev'])
                })
            data = {
                'draft_history': cleaned_history,
                'drafted_ids': [int(x) for x in self.drafted_ids]
            }
            with open(STATE_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving state to disk: {e}")

    def load_from_disk(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    data = json.load(f)
                self.draft_history = data.get('draft_history', [])
                self.drafted_ids = set(data.get('drafted_ids', []))
                
                # Rebuild roster for Jayme
                self.roster_manager.drafted_players = []
                for p in self.draft_history:
                    if p.get('drafted_by_jayme', False):
                        # Find player row
                        row = self.all_players_df[self.all_players_df['player_id'] == p['player_id']]
                        if not row.empty:
                            self.roster_manager.add_player(row.iloc[0])
            except Exception as e:
                print(f"Error loading state from disk: {e}")

    @property
    def current_pick(self):
        return len(self.draft_history) + 1

    @property
    def current_round(self):
        return min(self.total_rounds, ((self.current_pick - 1) // self.teams_count) + 1)

    @property
    def is_jayme_turn(self):
        return self.current_pick in self.jayme_picks

    @property
    def picks_until_next_turn(self):
        upcoming = [p for p in self.jayme_picks if p >= self.current_pick]
        if not upcoming:
            return 0
        return upcoming[0] - self.current_pick

    @property
    def current_drafter_name(self):
        if self.is_jayme_turn:
            return f"⭐ JAYME (Slot {self.jayme_slot}) ⭐"
        
        round_num = self.current_round
        pick_in_round = (self.current_pick - 1) % self.teams_count + 1
        if round_num % 2 == 1:
            slot = pick_in_round
        else:
            slot = self.teams_count - pick_in_round + 1
        return f"Team {slot}"

    def draft_player(self, player_id, for_jayme=False):
        """Marks player as drafted either for Jayme or by another rival."""
        if player_id in self.drafted_ids:
            return False
            
        row = self.all_players_df[self.all_players_df['player_id'] == player_id]
        if row.empty:
            return False
            
        player_row = row.iloc[0]
        self.drafted_ids.add(player_id)
        
        history_entry = {
            'pick_num': self.current_pick,
            'round_num': self.current_round,
            'player_id': player_id,
            'player_name': player_row['name'],
            'pos': player_row['pos'],
            'team': player_row['team'],
            'drafted_by_jayme': for_jayme,
            'context_ev': float(player_row['context_ev'])
        }
        self.draft_history.append(history_entry)
        
        if for_jayme:
            self.roster_manager.add_player(player_row)
            
        self.save_to_disk()
        return True

    def draft_custom_player(self, name, pos="RB", team="FA", for_jayme=False):
        """Adds and drafts an unlisted player on the fly."""
        existing = self.all_players_df[self.all_players_df['name'].str.lower() == name.lower()]
        if not existing.empty:
            p_id = existing.iloc[0]['player_id']
            return self.draft_player(p_id, for_jayme=for_jayme)
            
        max_df = int(self.all_players_df['player_id'].max()) if not self.all_players_df.empty else 0
        max_hist = max([int(x) for x in self.drafted_ids]) if self.drafted_ids else 0
        new_id = max(max_df, max_hist) + 1
        baseline = self.baselines.get(pos, 150.0)
        new_row = {
            'player_id': new_id,
            'name': name,
            'pos': pos,
            'team': team,
            'espn_adp': float(self.current_pick),
            'ecr': float(self.current_pick),
            'injury_risk': 'Low',
            'rush_att': 150 if pos == 'RB' else 0,
            'rush_yds': 700 if pos == 'RB' else 0,
            'rush_tds': 6 if pos == 'RB' else 0,
            'targets': 40 if pos in ['WR', 'TE', 'RB'] else 0,
            'rec': 30 if pos in ['WR', 'TE', 'RB'] else 0,
            'rec_yds': 350 if pos in ['WR', 'TE'] else 150,
            'rec_tds': 3 if pos in ['WR', 'TE'] else 1,
            'pass_yds': 3000 if pos == 'QB' else 0,
            'pass_tds': 20 if pos == 'QB' else 0,
            'pass_int': 10 if pos == 'QB' else 0,
            'fumbles': 1,
            'notes': f"Custom pick at #{self.current_pick}",
            'base_points': baseline,
            'context_multiplier': 1.0,
            'context_ev': baseline,
            'replacement_baseline': baseline,
            'vorp': 0.0,
            'true_ev_rank': len(self.all_players_df) + 1,
            'espn_value_delta': 0.0,
            'pos_rank': 99
        }
        self.all_players_df = pd.concat([self.all_players_df, pd.DataFrame([new_row])], ignore_index=True)
        return self.draft_player(new_id, for_jayme=for_jayme)

    def undo_last_pick(self):
        """Reverts the most recent draft pick."""
        if not self.draft_history:
            return None
            
        last = self.draft_history.pop()
        player_id = last['player_id']
        self.drafted_ids.discard(player_id)
        
        if last['drafted_by_jayme']:
            self.roster_manager.remove_player(last['player_name'])
            
        self.save_to_disk()
        return last

    def get_available_players_df(self, exclude_out=False):
        """Returns all undrafted players with dynamic marginal EV scores."""
        available = self.all_players_df[~self.all_players_df['player_id'].isin(self.drafted_ids)].copy()
        
        picks_gap = self.picks_until_next_turn
        marginal_evs = []
        role_labels = []
        
        for _, row in available.iterrows():
            m_ev, role = self.roster_manager.calculate_marginal_ev_addition(row, picks_until_next_turn=picks_gap)
            marginal_evs.append(m_ev)
            role_labels.append(role)
            
        available['marginal_ev'] = marginal_evs
        available['role_addition'] = role_labels
        
        if exclude_out:
            out_filter = ~available['injury_risk'].astype(str).str.upper().isin(['OUT']) & (available['marginal_ev'] > -500.0)
            available = available[out_filter]
        
        available = available.sort_values(by='marginal_ev', ascending=False).reset_index(drop=True)
        return available

    def get_tier_scarcity_summary(self):
        avail = self.get_available_players_df()
        summary = {}
        for pos in ['RB', 'WR', 'TE', 'QB']:
            pos_avail = avail[avail['pos'] == pos]
            top_tier = pos_avail[pos_avail['context_ev'] >= pos_avail['context_ev'].max() - 25.0] if not pos_avail.empty else []
            summary[pos] = {
                'total_remaining': len(pos_avail),
                'top_tier_remaining': len(top_tier),
                'best_available': pos_avail.iloc[0]['name'] if not pos_avail.empty else 'None',
                'best_ev': pos_avail.iloc[0]['context_ev'] if not pos_avail.empty else 0.0
            }
        return summary
