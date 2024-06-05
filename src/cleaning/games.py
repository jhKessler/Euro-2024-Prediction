import pandas as pd
from loguru import logger


def get_games(year: int) -> pd.DataFrame:
    try:
        group_games = pd.read_excel("data/manual/2020_matches.xlsx")
    except FileNotFoundError:
        logger.error(f"File not found for year {year} please run data generation script (refer to readme)")
        raise
    group_games[["team1_goals", "team2_goals"]] = group_games["result"].str.split("–", expand=True)
    group_games["team1_goals"] = group_games["team1_goals"].astype(int)
    group_games["team2_goals"] = group_games["team2_goals"].astype(int)
    group_games.drop(columns=["result"], inplace=True)
    group_games["team1"] = group_games["team1"].str.strip()
    group_games["team2"] = group_games["team2"].str.strip()
    return group_games


def merge_scores_and_flip(group_games: pd.DataFrame, country_scores: pd.DataFrame) -> pd.DataFrame:
    group_games = group_games.merge(country_scores, left_on="team1", right_on="Country", how="left").rename(columns={
        "MarketValue": "team1_market_value",
        "Country": "team1_country"
    }).merge(country_scores, left_on="team2", right_on="Country", how="left").rename(columns={
        "MarketValue": "team2_market_value",
        "Country": "team2_country"
    })
    group_games["market_value_distance"] = group_games["team1_market_value"] - group_games["team2_market_value"]
    flipped = group_games.copy()
    flipped = flipped.rename(columns={
        "team1_goals": "team2_goals",
        "team2_goals": "team1_goals",
    })[["team1_goals", "team2_goals", "market_value_distance"]]
    flipped["market_value_distance"] = -flipped["market_value_distance"]
    return pd.concat([flipped, group_games[["team1_goals", "team2_goals", "market_value_distance"]]], ignore_index=True)