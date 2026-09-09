import pytest
from src.config import load_league_config, get_jayme_pick_numbers
from src.engine import get_processed_player_pool
from src.state import DraftState

def test_league_config():
    config = load_league_config()
    assert config['teams_count'] == 14
    assert config['draft_position'] == 14
    assert config['scoring']['receiving']['reception'] == 1.0

def test_jayme_pick_numbers():
    picks = get_jayme_pick_numbers(teams_count=14, rounds=16, slot=14)
    assert len(picks) == 16
    assert picks[0] == 14
    assert picks[1] == 15
    assert picks[2] == 42
    assert picks[3] == 43

def test_player_pool_processing():
    df, baselines, adp_map = get_processed_player_pool()
    assert not df.empty
    assert 'context_ev' in df.columns
    assert 'vorp' in df.columns
    assert 'RB' in baselines
    assert 'WR' in baselines

def test_draft_state_operations():
    state = DraftState()
    initial_pick = state.current_pick
    assert initial_pick >= 1
