from argparse import ArgumentParser
import pandas as pd
import cleaning
import os
from loguru import logger

def format_training_data(year: int):
    os.makedirs("data/cleaned/", exist_ok=True)
    games = cleaning.get_games(year)
    team_market_value_scores = cleaning.get_team_market_value_scores(year)
    data = cleaning.merge_scores(games, team_market_value_scores)
    data = cleaning.flip_and_duplicate(data)
    data.to_csv(f"data/cleaned/{year}_train_games.csv", sep=";", index=False)
    logger.info(f"Saved cleaned training data for {year} to data/cleaned/{year}_train_games.csv")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--years", type=int, nargs="+", help="Years of the tournaments to gather or format data for (must be valid euro year, e.g. 2020, 2024, etc.)"
    )
    args = parser.parse_args()

    for year in args.years:
        format_training_data(year)