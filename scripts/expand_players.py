import pandas as pd

df = pd.read_csv('data/players.csv')
df.loc[df['name'] == 'Kansas City Chiefs', 'pos'] = 'DST'
df.loc[df['name'] == 'Kansas City Chiefs', 'team'] = 'KC'

more_players = [
    # Additional QBs
    ("Daniel Jones", "QB", "NYG", 180.0, 175.0, "Medium", 65, 360, 2, 0, 0, 0, 0, 3100, 16, 12, "Starting job on line, rushing baseline with Nabers."),
    ("Bryce Young", "QB", "CAR", 185.0, 178.0, "Low", 40, 210, 1, 0, 0, 0, 0, 3350, 18, 12, "Dave Canales QB whisperer effect."),
    ("Drake Maye", "QB", "NE", 195.0, 185.0, "Low", 50, 260, 2, 0, 0, 0, 0, 2900, 15, 12, "Rookie with Josh Allen athletic profile."),
    ("Sam Darnold", "QB", "MIN", 190.0, 188.0, "Low", 30, 120, 1, 0, 0, 0, 0, 3600, 22, 13, "Kevin O'Connell scheme with Jefferson & Addison."),
    ("Russell Wilson", "QB", "PIT", 182.0, 182.0, "Low", 35, 150, 1, 0, 0, 0, 0, 3100, 19, 9, "Arthur Smith run-heavy scheme, competing with Fields."),
    ("Justin Fields", "QB", "PIT", 175.0, 170.0, "Low", 70, 420, 4, 0, 0, 0, 0, 1800, 11, 7, "Package plays / potential starter with elite rushing ceiling."),
    
    # Additional RBs
    ("Alexander Mattison", "RB", "LV", 187.0, 179.0, "Low", 110, 430, 2, 25, 20, 140, 1, 0, 0, 0, "Backup to Zamir White in Las Vegas."),
    ("Ty Chandler", "RB", "MIN", 161.0, 150.0, "Low", 120, 530, 3, 30, 24, 180, 1, 0, 0, 0, "Change of pace runner behind Aaron Jones with 4.38 speed."),
    ("Miles Sanders", "RB", "CAR", 198.0, 189.0, "Low", 90, 360, 2, 25, 18, 130, 0, 0, 0, 0, "Veteran reserve behind Chuba Hubbard and Brooks."),
    ("Kenneth Gainwell", "RB", "PHI", 205.0, 195.0, "Low", 70, 310, 2, 30, 24, 170, 0, 0, 0, 0, "Two-minute drill pass protector behind Barkley."),
    ("Roschon Johnson", "RB", "CHI", 188.0, 181.0, "Low", 90, 390, 3, 25, 20, 150, 1, 0, 0, 0, "Short-yardage thumper in Chicago backfield."),
    ("Justice Hill", "RB", "BAL", 202.0, 192.0, "Low", 60, 280, 1, 35, 28, 210, 1, 0, 0, 0, "Ravens primary 3rd down passing back."),
    ("Samaje Perine", "RB", "KC", 196.0, 186.0, "Low", 60, 260, 1, 35, 30, 220, 1, 0, 0, 0, "Signed by Chiefs for crucial 3rd-down pass protection with Mahomes."),
    ("Elijah Mitchell", "RB", "SF", 215.0, 200.0, "High", 70, 320, 2, 10, 8, 50, 0, 0, 0, 0, "Injury prone backup to McCaffrey."),
    ("Jordan Mason", "RB", "SF", 193.0, 165.0, "Low", 110, 520, 4, 15, 10, 80, 0, 0, 0, 0, "DIRECT MCCAFFREY HANDCUFF. Shined all preseason; RB1 if CMC rests."),
    ("Keaontay Ingram", "RB", "KC", 220.0, 210.0, "Low", 40, 160, 1, 10, 8, 50, 0, 0, 0, 0, "Depth runner for Chiefs."),
    ("Audric Estime", "RB", "DEN", 204.0, 194.0, "Low", 70, 310, 3, 10, 8, 50, 0, 0, 0, 0, "Sean Payton goal-line bruiser."),
    ("Isaac Guerendo", "RB", "SF", 218.0, 205.0, "Low", 50, 240, 2, 10, 8, 60, 0, 0, 0, 0, "4.33 speed rookie runner in Shanahan system."),
    ("Tyrone Tracy Jr.", "RB", "NYG", 194.0, 176.0, "Low", 80, 350, 2, 30, 24, 190, 1, 0, 0, 0, "Converted college WR with explosive PPR passing profile behind Singletary."),
    ("Cam Akers", "RB", "HOU", 212.0, 202.0, "Medium", 70, 290, 2, 15, 12, 80, 0, 0, 0, 0, "Depth behind Mixon and Pierce."),
    ("D'Onta Foreman", "RB", "CLE", 208.0, 199.0, "Low", 80, 340, 3, 10, 8, 50, 0, 0, 0, 0, "Veteran bruiser for early downs while Chubb is out."),
    ("Tank Bigsby", "RB", "JAX", 200.0, 190.0, "Low", 75, 320, 2, 10, 8, 50, 0, 0, 0, 0, "Improved sophomore season behind Etienne."),

    # Additional WRs
    ("Gabe Davis", "WR", "JAX", 152.0, 148.0, "Low", 0, 0, 0, 75, 42, 680, 5, 0, 0, 0, "Deep post specialist in Doug Pederson offense."),
    ("Kendrick Bourne", "WR", "NE", 201.0, 196.0, "Medium", 0, 0, 0, 70, 48, 550, 3, 0, 0, 0, "Starting on PUP; veteran target for Patriots."),
    ("Jalen Tolbert", "WR", "DAL", 191.0, 184.0, "Low", 0, 0, 0, 70, 45, 580, 4, 0, 0, 0, "Won starting WR3 job in Dallas high-pass offense."),
    ("Andrei Iosivas", "WR", "CIN", 183.0, 172.0, "Low", 0, 0, 0, 65, 45, 540, 5, 0, 0, 0, "Takes over Tyler Boyd starting slot role in Burrow offense."),
    ("Tre Tucker", "WR", "LV", 207.0, 201.0, "Low", 0, 0, 0, 55, 35, 480, 2, 0, 0, 0, "Field stretcher opposite Adams and Meyers."),
    ("Michael Wilson", "WR", "ARI", 174.0, 168.0, "Low", 0, 0, 0, 75, 48, 620, 4, 0, 0, 0, "Boundary contested catch receiver outside Harrison Jr."),
    ("Darius Slayton", "WR", "NYG", 197.0, 191.0, "Low", 0, 0, 0, 65, 40, 610, 3, 0, 0, 0, "Deep vertical route runner in NY."),
    ("Quentin Johnston", "WR", "LAC", 189.0, 187.0, "Low", 0, 0, 0, 70, 42, 540, 3, 0, 0, 0, "Former 1st round pick looking for bounce-back."),
    ("Greg Dortch", "WR", "ARI", 186.0, 177.0, "Low", 0, 0, 0, 75, 55, 520, 2, 0, 0, 0, "Full PPR slot favorite for Kyler Murray."),
    ("Jermaine Burton", "WR", "CIN", 192.0, 180.0, "Low", 0, 0, 0, 55, 34, 510, 4, 0, 0, 0, "Dynamic rookie deep threat with Joe Burrow."),
    ("Malachi Corley", "WR", "NYJ", 203.0, 197.0, "Low", 0, 0, 0, 55, 38, 420, 2, 0, 0, 0, "YAC King rookie slot receiver for Rodgers."),
    ("Devontez Walker", "WR", "BAL", 217.0, 209.0, "Low", 0, 0, 0, 45, 25, 380, 2, 0, 0, 0, "Deep vertical speed for Ravens."),
    ("Ricky Pearsall", "WR", "SF", 162.0, 163.0, "Medium", 0, 0, 0, 55, 36, 450, 2, 0, 0, 0, "Rookie 1st rounder; stash for late-season Shanahan role."),
    ("Jalen McMillan", "WR", "TB", 199.0, 183.0, "Low", 0, 0, 0, 60, 40, 520, 3, 0, 0, 0, "Sensational training camp; earned WR3 slot in Tampa."),
    ("Luke McCaffrey", "WR", "WAS", 209.0, 198.0, "Low", 0, 0, 0, 60, 42, 480, 2, 0, 0, 0, "Jahan Dotson trade opens up immediate slot reps."),
    ("Roman Wilson", "WR", "PIT", 214.0, 206.0, "Low", 0, 0, 0, 50, 32, 420, 2, 0, 0, 0, "Rookie slot receiver in Pittsburgh."),

    # Additional TEs
    ("Noah Fant", "TE", "SEA", 181.0, 174.0, "Low", 0, 0, 0, 65, 46, 510, 3, 0, 0, 0, "Parkinson/Dissly gone; full-time TE in Grubb pass offense."),
    ("Juwan Johnson", "TE", "NO", 184.0, 181.0, "Low", 0, 0, 0, 60, 42, 450, 4, 0, 0, 0, "Athletic red zone favorite for Carr."),
    ("Colby Parkinson", "TE", "LAR", 206.0, 193.0, "Low", 0, 0, 0, 55, 38, 420, 3, 0, 0, 0, "Tyler Higbee starting on PUP; Parkinson starts in McVay offense."),
    ("Zach Ertz", "TE", "WAS", 210.0, 203.0, "Low", 0, 0, 0, 55, 38, 380, 3, 0, 0, 0, "Veteran security blanket for Jayden Daniels."),
    ("Greg Dulcich", "TE", "DEN", 211.0, 204.0, "Medium", 0, 0, 0, 55, 36, 410, 3, 0, 0, 0, "Joker TE in Sean Payton offense."),
    ("Theo Johnson", "TE", "NYG", 219.0, 208.0, "Low", 0, 0, 0, 50, 32, 360, 2, 0, 0, 0, "Darren Waller retired; freak 9.99 RAS rookie."),

    # Additional D/ST
    ("Philadelphia Eagles", "DST", "PHI", 195.0, 190.0, "Low", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Vic Fangio defense with revamped secondary."),
    ("Denver Broncos", "DST", "DEN", 205.0, 200.0, "Low", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Patrick Surtain lockdown pass defense."),
    ("Chicago Bears", "DST", "CHI", 210.0, 202.0, "Low", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Montez Sweat turnover-forcing defense."),
    ("Green Bay Packers", "DST", "GB", 213.0, 205.0, "Low", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Jeff Hafley aggressive attacking scheme."),
    ("Indianapolis Colts", "DST", "IND", 216.0, 207.0, "Low", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Strong front four with DeForest Buckner & Latu."),

    # Additional Kickers
    ("Cairo Santos", "K", "CHI", 200.0, 195.0, "Low", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Reliable kicker in upgraded offense."),
    ("Chase McLaughlin", "K", "TB", 204.0, 198.0, "Low", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Huge leg; 7-of-8 from 50+ yards."),
    ("Dustin Hopkins", "K", "CLE", 208.0, 201.0, "Low", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Elite 50+ yard weapon in Cleveland."),
    ("Matt Gay", "K", "IND", 212.0, 203.0, "Low", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Steichen offense drives deep into opponent territory."),
    ("Blake Grupe", "K", "NO", 215.0, 206.0, "Low", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "Indoor kicker with high attempt volume.")
]

new_rows = []
for item in more_players:
    name, pos, team, espn, ecr, inj, r_att, r_yds, r_td, tgts, rec, rec_yds, rec_td, p_yds, p_td, p_int, notes = item
    new_rows.append({
        "name": name, "pos": pos, "team": team, "espn_adp": espn, "ecr": ecr, "injury_risk": inj,
        "rush_att": r_att, "rush_yds": r_yds, "rush_tds": r_td, "targets": tgts, "rec": rec,
        "rec_yds": rec_yds, "rec_tds": rec_td, "pass_yds": p_yds, "pass_tds": p_td, "pass_int": p_int,
        "fumbles": 1 if pos in ["RB", "QB"] else 0, "notes": notes
    })

df_more = pd.DataFrame(new_rows)
df_combined = pd.concat([df, df_more], ignore_index=True).drop_duplicates(subset=['name'], keep='first')
df_combined['player_id'] = range(1, len(df_combined) + 1)
df_combined.to_csv('data/players.csv', index=False)
print(f"Total players after expansion: {len(df_combined)}")
