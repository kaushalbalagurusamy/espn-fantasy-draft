with open("src/state.py", "r") as f:
    text = f.read()

# Replace json dump logic to ensure all ints and floats are native python types
old_save = """    def save_to_disk(self):
        try:
            data = {
                'draft_history': self.draft_history,
                'drafted_ids': list(self.drafted_ids)
            }
            with open(STATE_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving state to disk: {e}")"""

new_save = """    def save_to_disk(self):
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
            print(f"Error saving state to disk: {e}")"""

text = text.replace(old_save, new_save)
with open("src/state.py", "w") as f:
    f.write(text)
print("Updated src/state.py with native int/float serialization!")
