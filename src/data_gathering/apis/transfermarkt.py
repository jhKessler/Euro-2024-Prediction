import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

def _market_value_from_id(id: str, year: int = None) -> int:
    url = f"https://www.transfermarkt.com/ceapi/marketValueDevelopment/graph/{str(id)}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if not r.ok:
        raise ValueError(f"Failed to get market value for player with id {id}")
    data = json.loads(r.text)["list"]
    if year is None:
        return data[-1]["y"]
    as_df = pd.DataFrame(data)
    only_specified_year = as_df[as_df.datum_mw.str.endswith(str(year))]
    if only_specified_year.empty:
        try:
            only_previous_year = as_df[as_df.datum_mw.str.endswith(str(year-1))]
        except Exception as e:
            raise ValueError(f"Failed to get market value for player with id {id}")
        return only_previous_year.iloc[-1]["y"]
    return only_specified_year["y"].mean()


def _id_from_name(name: str) -> int:
    url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={name}"

    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if not r.ok:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        raise ValueError(f"Failed to get id for player with name {name}")
    soup = BeautifulSoup(r.text, "lxml")
    try:
        return int(soup.find(class_="keys").find("span").text)
    except Exception:
        raise ValueError(f"Failed to get id for player with name {name}")


def get_player_market_value(name: str, year: int = None) -> int:
    id = _id_from_name(name)
    return _market_value_from_id(id, year)
