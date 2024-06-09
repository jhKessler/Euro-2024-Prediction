from .games import get_games
from .teams import get_team_market_value_scores


def clean_data(year: int, is_inference: bool):
    market_values = get_team_market_value_scores(year)
    market_values.to_csv(f"data/cleaned/{year}_market_values.csv", sep=";", index=False)

    games = get_games(year, market_values, is_inference)
    games.to_csv(f"data/cleaned/{year}_games.csv", sep=";", index=False)