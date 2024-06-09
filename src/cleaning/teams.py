import pandas as pd
from loguru import logger


def get_team_market_value_scores(year: int) -> pd.DataFrame:
    """Gets the market value coefficients for each country based on the average market value of the players in the tournament

    calculation for a teams coefficient is
    average_player_cost_of_team / max_average_player_cost_over_all_teams
    so it's between 0 and 1 where 1 is the most expensive team in the tournament

    Args:
        year (int):

    Returns:
        pd.DataFrame: dataframe with columns:
        Country (str): name of the country
        MarketValue (float): coefficient for the country
    """
    try:
        data = pd.read_csv(f"data/raw/{year}_players_with_market_value.csv", sep=";")
    except FileNotFoundError:
        raise ValueError(f"data/raw/{year}_players_with_market_value.csv not found for year {year} please run data generation script (refer to readme)")
    data.dropna(subset=["MarketValue"], inplace=True)
    average_player_cost = data.groupby("Country")["MarketValue"].mean().astype(int)
    average_play_cost_coefficient = average_player_cost / average_player_cost.max()
    country_scores = average_play_cost_coefficient.to_frame().reset_index()
    country_scores["Country"] = country_scores["Country"].str.strip()
    return country_scores
