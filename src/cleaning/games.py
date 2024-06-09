import pandas as pd
from loguru import logger



def flip_and_duplicate(games: pd.DataFrame) -> pd.DataFrame:
    """Duplicates each game with the teams flipped
    so e.g. "turkey vs italy (0-1)" becomes "italy vs turkey (1-0)", this is done so that the model does not care about the order of the teams
    and can learn that the market value difference between the two teams is what matters

    Args:
        games (pd.DataFrame): games df from merge_scores

    Returns:
        pd.DataFrame: _description_
    """
    flipped = games.copy()
    flipped = flipped.rename(
        columns={
            "team1_goals": "team2_goals",
            "team2_goals": "team1_goals",
            "team1": "team2",
            "team2": "team1",
        }
    )
    return pd.concat(
        [flipped, games],
        ignore_index=True,
    )

def add_market_value_distance(games: pd.DataFrame, market_values: pd.DataFrame) -> pd.DataFrame:
    games = games.merge(market_values, left_on="team1", right_on="Country", how="left") \
                .merge(market_values, left_on="team2", right_on="Country", how="left", suffixes=("_team1", "_team2"))
    games["team1_market_value_distance"] = (games["MarketValue_team1"]-games["MarketValue_team2"])
    games["team2_market_value_distance"] = (-games["team1_market_value_distance"])
    return games.drop(columns=["MarketValue_team1", "MarketValue_team2", "Country_team1", "Country_team2"])


def get_games(year: int, market_values: pd.DataFrame, is_inference: bool) -> pd.DataFrame:
    """Gets and formats all games of a certain tournament

    Args:
        year (int): _description_

    Returns:
        pd.DataFrame: dataframe with all games of the tournament, having columns:
        team1 (str): name of the first team
        team2 (str): name of the second team
        group (str): group of the game, None if knockout stage
        if available: 
        team1_goals (int): goals scored by team1
        team2_goals (int): goals scored by team2
    """
    try:
        games = pd.read_excel(f"data/manual/{year}_matches.xlsx")
    except FileNotFoundError:
        logger.error(
            f"File not found for year {year} please run raw data generation script (refer to readme)"
        )
        raise
    games["team1"] = games["team1"].str.strip()
    games["team2"] = games["team2"].str.strip()

    if "result" not in games.columns or is_inference:
        return add_market_value_distance(games[["team1", "team2", "group"]], market_values) # no results available
    
    games[["team1_goals", "team2_goals"]] = games["result"].str.split("–", expand=True)
    games["team1_goals"] = games["team1_goals"].astype(int)
    games["team2_goals"] = games["team2_goals"].astype(int)

    if not is_inference:
        games = flip_and_duplicate(games)
    
    games = add_market_value_distance(games, market_values)
    return games[['team1', 'team2', 'group', 'team1_goals', 'team2_goals', 'team1_market_value_distance', 'team2_market_value_distance']]