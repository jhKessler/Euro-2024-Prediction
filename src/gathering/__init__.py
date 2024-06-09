

import os
import time

import numpy as np
import pandas as pd

from .apis import transfermarkt
from .scraping import wikipedia

from loguru import logger


def gather_tournament_data(year: int, timeout_seconds: int, continue_gathering: bool):
    os.makedirs("data/raw/", exist_ok=True)
    all_players = wikipedia.get_all_players(year)
    all_players.to_csv(f"data/raw/{year}_players.csv", index=False)
    start_index = 0
    if continue_gathering:
        # get the last player that was gathered
        previous_data = pd.read_csv(
            f"data/raw/{year}_players_with_market_value.csv",
            sep=";",
        )
        last_player = previous_data.iloc[-1]
        filt = (all_players["Country"] == last_player["Country"]) & (
            all_players["Player"] == last_player["Player"]
        )
        start_index = (np.where(filt)[0])[0] + 1
        logger.info(
            f"Continuing gathering from index {start_index}, player {last_player['Player']}"
        )

    for index, (_, player) in enumerate(
        all_players.iloc[start_index:].iterrows(), start=start_index
    ):
        time.sleep(timeout_seconds)
        try:
            market_value = transfermarkt.get_player_market_value(player["Player"], year)
            logger.info(
                f"Market value for '{player['Player']}' ({player["Country"]}): {market_value}"
            )
        except Exception as e:
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
            mode="w" if index == 0 else "a",
        )
