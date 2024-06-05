import os
import time
from argparse import ArgumentParser

from data_gathering import transfermarkt, wikipedia
from loguru import logger


def build_tournament_data(year: int, timeout_seconds: int = 10):
    all_players = wikipedia.get_all_players(year)
    all_players.to_csv(f"data/raw/{year}_players.csv", index=False)

    for index, (_, player) in enumerate(all_players.iterrows()):
        time.sleep(timeout_seconds)
        try:
            market_value = transfermarkt.get_player_market_value(player["Player"], year)
            logger.info(
                f"Market value for '{player['Player']}' ({player["Country"]}): {market_value}"
            )
        except ValueError as e:
            logger.error(
                f"Failed to get market value for '{player['Player']}' ({player["Country"]}): {e}"
            )
            continue
        player["MarketValue"] = market_value
        player.to_frame().T.to_csv(
            f"data/raw/{year}_players_with_market_value.csv", 
            index=False, 
            sep=";",
            header=(index == 0),
            mode="w" if index == 0 else "a"
        )



if __name__ == "__main__":
    os.makedirs("data/raw/", exist_ok=True)
    parser = ArgumentParser()
    parser.add_argument(
        "--year", type=int, required=True, help="Year of the tournament"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Number of seconds to wait between requests, use at own caution!",
    )
    args = parser.parse_args()

    build_tournament_data(args.year)
