import pandas as pd
from .group_phase import simulate_group_phase

def simulate_tournament(group_games: pd.DataFrame):
    group_phase_result = simulate_group_phase()