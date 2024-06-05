import pandas as pd
from loguru import logger

def get_team_market_value_scores(year: int) -> pd.DataFrame:
    try: 
        data = pd.read_csv(f"data/raw/{year}_players_with_market_value.csv", sep=";")
    except FileNotFoundError:
        logger.error(f"File not found for year {year} please run data generation script (refer to readme)")
        raise
    data.dropna(
        subset=["MarketValue"],
        inplace=True
    )
    average_player_cost = (
        data.groupby("Country")["MarketValue"]
        .mean()
        .astype(int)
    )
    average_play_cost_coefficient = average_player_cost / average_player_cost.max()
    country_scores = average_play_cost_coefficient.to_frame().reset_index()
    country_scores["Country"] = country_scores["Country"].str.strip()
    return country_scores
