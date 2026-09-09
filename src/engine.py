import pandas as pd
import numpy as np
import os
from .config import load_league_config

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_raw_data():
    players_df = pd.read_csv(os.path.join(DATA_DIR, "players.csv"))
    teams_df = pd.read_csv(os.path.join(DATA_DIR, "team_context.csv"))
    if 'name' in teams_df.columns:
        teams_df = teams_df.rename(columns={'name': 'team_full_name'})
    return players_df, teams_df

def calculate_base_projections(df, scoring_rules):
    """
    Calculate baseline fantasy points using exact ESPN Full-PPR scoring rules from screenshots.
    """
    pass_pts = (
        df['pass_yds'] * scoring_rules['passing']['yards'] +
        df['pass_tds'] * scoring_rules['passing']['td'] +
        df['pass_int'] * scoring_rules['passing']['interception']
    )
    rush_pts = (
        df['rush_yds'] * scoring_rules['rushing']['yards'] +
        df['rush_tds'] * scoring_rules['rushing']['td']
    )
    # Full PPR: 1.0 pt per reception!
    rec_pts = (
        df['rec'] * scoring_rules['receiving']['reception'] +
        df['rec_yds'] * scoring_rules['receiving']['yards'] +
        df['rec_tds'] * scoring_rules['receiving']['td']
    )
    fumble_pts = df['fumbles'] * scoring_rules['fumbles_lost']
    
    total_pts = pass_pts + rush_pts + rec_pts + fumble_pts
    
    # Baseline for DST and K
    for idx, row in df.iterrows():
        if row['pos'] == 'DST':
            total_pts.loc[idx] = 115.0 - (row['espn_adp'] - 140.0) * 0.4
        elif row['pos'] == 'K':
            total_pts.loc[idx] = 130.0 - (row['espn_adp'] - 150.0) * 0.3
            
    df['base_points'] = total_pts.round(1)
    return df

def apply_contextual_multipliers(df, teams_df):
    """
    Adjusts base projections with Health, Offensive Line, Vegas Implied Totals,
    and Coaching Pace/Scheme factors.
    """
    merged = df.merge(teams_df, on='team', how='left')
    
    merged['vegas_implied_pts'] = merged['vegas_implied_pts'].fillna(22.0)
    merged['oline_run_grade'] = merged['oline_run_grade'].fillna(75.0)
    merged['oline_pass_grade'] = merged['oline_pass_grade'].fillna(75.0)
    merged['pass_rate_over_exp'] = merged['pass_rate_over_exp'].fillna(0.0)
    merged['rb_committee_factor'] = merged['rb_committee_factor'].fillna(0.35)
    
    # 1. Health Multiplier
    health_map = {
        "Low": 1.00,
        "Medium": 0.94,     # Small penalty for nagging soft tissue history
        "High": 0.84,       # History of major ailments
        "Questionable": 0.95,# Minor ding, active
        "PUP": 0.50,        # On PUP list, misses half season
        "PUP/IR": 0.40,     # Reserve PUP/IR
        "IR": 0.30,         # On Injured Reserve (misses significant time)
        "OUT": 0.0          # OUT / Unsigned / Injured
    }
    m_health = merged['injury_risk'].map(health_map).fillna(1.0)
    
    # 2. Team Implied Scoring Multiplier (High scoring offenses create more red zone trips)
    m_vegas = 1.0 + (merged['vegas_implied_pts'] - 22.5) * 0.015
    
    # 3. Offensive Line Multiplier
    m_oline = pd.Series(1.0, index=merged.index)
    rb_mask = merged['pos'] == 'RB'
    m_oline[rb_mask] = 1.0 + (merged.loc[rb_mask, 'oline_run_grade'] - 77.0) * 0.005
    pass_mask = merged['pos'].isin(['QB', 'WR'])
    m_oline[pass_mask] = 1.0 + (merged.loc[pass_mask, 'oline_pass_grade'] - 77.0) * 0.003
    
    # 4. Scheme & Coaching Multiplier
    m_scheme = pd.Series(1.0, index=merged.index)
    m_scheme[pass_mask] = 1.0 + merged.loc[pass_mask, 'pass_rate_over_exp'] * 0.7
    m_scheme[rb_mask] = 1.0 + (0.35 - merged.loc[rb_mask, 'rb_committee_factor']) * 0.3
    
    # Combine all multipliers
    total_mult = m_health * m_vegas * m_oline * m_scheme
    merged['context_multiplier'] = total_mult.round(3)
    merged['context_ev'] = (merged['base_points'] * total_mult).round(1)
    
    # Force 0.0 EV for any OUT player
    out_mask = merged['injury_risk'].astype(str).str.upper().isin(['OUT'])
    merged.loc[out_mask, 'context_ev'] = 0.0
    
    return merged

def calculate_vorp_and_arbitrage(df, teams_count=14):
    """
    Computes Value Over Replacement Player (VORP) specifically calibrated
    for a 14-team league starting 1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX.
    """
    replacement_ranks = {
        'QB': 15,    # 14 starters + 1
        'RB': 36,    # 28 starters + 8 flex starters
        'WR': 36,    # 28 starters + 8 flex starters
        'TE': 15,    # 14 starters + 1
        'DST': 15,   # 14 starters + 1
        'K': 15      # 14 starters + 1
    }
    
    baselines = {}
    for pos, rank in replacement_ranks.items():
        pos_df = df[df['pos'] == pos].sort_values(by='context_ev', ascending=False)
        if len(pos_df) >= rank:
            baselines[pos] = pos_df.iloc[rank - 1]['context_ev']
        elif len(pos_df) > 0:
            baselines[pos] = pos_df.iloc[-1]['context_ev'] * 0.85
        else:
            baselines[pos] = 0.0

    df['replacement_baseline'] = df['pos'].map(baselines)
    df['vorp'] = (df['context_ev'] - df['replacement_baseline']).round(1)
    
    # Bottom out VORP for OUT players
    out_mask = df['injury_risk'].astype(str).str.upper().isin(['OUT'])
    df.loc[out_mask, 'vorp'] = -999.0
    
    # Overall True EV Rank
    df = df.sort_values(by='vorp', ascending=False).reset_index(drop=True)
    df['true_ev_rank'] = range(1, len(df) + 1)
    
    # Arbitrage Value Delta = ESPN ADP - True EV Rank
    df['espn_value_delta'] = (df['espn_adp'] - df['true_ev_rank']).round(1)
    
    # Positional Rank
    df['pos_rank'] = df.groupby('pos')['context_ev'].rank(ascending=False, method='min').astype(int)
    
    return df, baselines

def get_processed_player_pool():
    cfg = load_league_config()
    players_df, teams_df = load_raw_data()
    players_with_base = calculate_base_projections(players_df, cfg['scoring'])
    players_with_context = apply_contextual_multipliers(players_with_base, teams_df)
    processed_df, baselines = calculate_vorp_and_arbitrage(players_with_context, cfg['teams_count'])
    return processed_df, baselines, cfg
