import pandas as pd
from loguru import logger


def get_games(year: int) -> pd.DataFrame:
    """Gets and formats all games of a certain tournament

    Args:
        year (int): _description_

    Returns:
        pd.DataFrame: dataframe with all games of the tournament, having columns:
        team1 (str): name of the first team
        team2 (str): name of the second team
        result (str): result of the game in the format "team1_goals–team2_goals"

    """
    try:
        games = pd.read_excel(f"data/manual/{year}_matches.xlsx")
    except FileNotFoundError:
        logger.error(f"File not found for year {year} please run raw data generation script (refer to readme)")
        raise
    games[["team1_goals", "team2_goals"]] = games["result"].str.split("–", expand=True)
    games["team1_goals"] = games["team1_goals"].astype(int)
    games["team2_goals"] = games["team2_goals"].astype(int)
    games.drop(columns=["result"], inplace=True)
    games["team1"] = games["team1"].str.strip()
    games["team2"] = games["team2"].str.strip()
    return games


def merge_scores(games: pd.DataFrame, country_scores: pd.DataFrame) -> pd.DataFrame:
    """Adds market value coefficients to the games dataframe, and duplicates each game with the teams flipped
    so e.g. "turkey vs italy (0-1)" becomes "italy vs turkey (1-0)", this is done so that the model does not care about the order of the teams
    and can learn that the market value difference between the two teams is what matters

    Args:
        games (pd.DataFrame): games df from get_games
        country_scores (pd.DataFrame): dataframe with the market coeffecients for each country (from cleaning/teams.py get_team_market_value_scores)

    Returns:
        pd.DataFrame: _description_
    """
    games = games.merge(country_scores, left_on="team1", right_on="Country", how="left").rename(columns={
        "MarketValue": "team1_market_value",
        "Country": "team1_country"
    }).merge(country_scores, left_on="team2", right_on="Country", how="left").rename(columns={
        "MarketValue": "team2_market_value",
        "Country": "team2_country"
    })
    games["market_value_distance"] = games["team1_market_value"] - games["team2_market_value"]
    return games


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
    flipped = flipped.rename(columns={
        "team1_goals": "team2_goals",
        "team2_goals": "team1_goals",
    })[["team1_goals", "team2_goals", "market_value_distance"]]
    flipped["market_value_distance"] = -flipped["market_value_distance"]
    return pd.concat([flipped, games[["team1_goals", "team2_goals", "market_value_distance"]]], ignore_index=True)