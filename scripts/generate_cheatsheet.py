import pandas as pd
from src.engine import get_processed_player_pool

df, baselines, cfg = get_processed_player_pool()

with open("cheatsheet_turn14.md", "w") as f:
    f.write("# 🏈 Jayme's Draft Cheat Sheet: Slot #14 Turn Strategy\n\n")
    f.write("**Format:** 14-Team Full-PPR | **Roster:** 1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX, 1 DST, 1 K, 7 Bench\n\n")
    f.write("---\n\n")
    
    f.write("## 🏆 Round-by-Round Turn Targets\n\n")
    
    turn_pairs = [
        ("Turn 1 (Picks 14 & 15)", 10, 20),
        ("Turn 2 (Picks 42 & 43)", 35, 50),
        ("Turn 3 (Picks 70 & 71)", 62, 78),
        ("Turn 4 (Picks 98 & 99)", 90, 108),
        ("Turn 5 (Picks 126 & 127)", 118, 136),
        ("Turn 6 (Picks 154 & 155)", 145, 165),
        ("Turn 7 (Picks 182 & 183)", 175, 195),
        ("Turn 8 (Picks 210 & 211)", 200, 225),
    ]
    
    for label, min_adp, max_adp in turn_pairs:
        f.write(f"### {label}\n")
        targets = df[(df['espn_adp'] >= min_adp) & (df['espn_adp'] <= max_adp)].sort_values(by='vorp', ascending=False).head(5)
        f.write("| Player | Pos | Team | Context EV | VORP | ESPN ADP | Arbitrage Delta | Strategic Note |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for _, r in targets.iterrows():
            f.write(f"| **{r['name']}** | {r['pos']} | {r['team']} | {r['context_ev']:.1f} | {r['vorp']:.1f} | {r['espn_adp']:.1f} | +{r['espn_value_delta']:.0f} | {r['notes'][:45]}... |\n")
        f.write("\n")

    f.write("---\n\n")
    f.write("## 💎 Top 10 ESPN Value Steals (Buried in ESPN Queue)\n\n")
    steals = df.sort_values(by='espn_value_delta', ascending=False).head(10)
    f.write("| Rank | Player | Pos | Team | True EV Rank | ESPN ADP | Steal Delta | Context Note |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for idx, (_, r) in enumerate(steals.iterrows(), 1):
        f.write(f"| #{idx} | **{r['name']}** | {r['pos']} | {r['team']} | #{r['true_ev_rank']} | {r['espn_adp']:.1f} | **+{r['espn_value_delta']:.0f}** | {r['notes']} |\n")
        
    f.write("\n---\n\n")
    f.write("## ⚠️ Top ESPN Traps / Reaches to Avoid\n\n")
    fades = df[df['espn_adp'] <= 70].sort_values(by='espn_value_delta', ascending=True).head(8)
    f.write("| Player | Pos | Team | True EV Rank | ESPN ADP | Overpriced Delta | Red Flag Reason |\n")
    f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for _, r in fades.iterrows():
        f.write(f"| **{r['name']}** | {r['pos']} | {r['team']} | #{r['true_ev_rank']} | {r['espn_adp']:.1f} | {r['espn_value_delta']:.0f} | Low VORP relative to ADP; better options available at the turn. |\n")

print("Generated cheatsheet_turn14.md successfully!")
