from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_all_players(year: int = 2024) -> pd.DataFrame:
    url = f"https://en.wikipedia.org/wiki/UEFA_Euro_{year}_squads"
    r = requests.get(url)
    if not r.ok:
        raise Exception(f"Failed to fetch {url}")
    teams = pd.read_html(StringIO(r.text))[:24]
    soup = BeautifulSoup(r.text, "lxml")
    country_order = [s.text.replace("[edit]", "") for s in soup.find_all("h3")][:24]
    for country, team in zip(country_order, teams):
        team["Country"] = country
    teams = pd.concat(teams).dropna(subset=["No."])
    teams["Player"] = teams["Player"].str.replace(r'\(.*?\)', '', regex=True).str.strip()
    return teams
