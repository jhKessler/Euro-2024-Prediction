import pandas as pd
from .interfaces import GroupStageResult

third_places_advance_dict = {
    ("A", "B", "C", "D"): ("A", "D", "B", "C"),
    ("A", "B", "C", "E"): ("A", "E", "B", "C"),
    ("A", "B", "C", "F"): ("A", "F", "B", "C"),
    ("A", "B", "D", "E"): ("D", "E", "A", "B"),
    ("A", "B", "D", "F"): ("D", "F", "A", "B"),
    ("A", "B", "E", "F"): ("E", "F", "B", "A"),
    ("A", "C", "D", "E"): ("E", "D", "C", "A"),
    ("A", "C", "D", "F"): ("F", "D", "C", "A"),
    ("A", "C", "E", "F"): ("E", "F", "C", "A"),
    ("A", "D", "E", "F"): ("E", "F", "D", "A"),
    ("B", "C", "D", "E"): ("E", "D", "B", "C"),
    ("B", "C", "D", "F"): ("F", "D", "C", "B"),
    ("B", "C", "E", "F"): ("F", "E", "C", "B"),
    ("B", "D", "E", "F"): ("F", "E", "D", "B"),
    ("C", "D", "E", "F"): ("F", "E", "D", "C"),
}

against = ("B", "C", "E", "F")


def get_team_name(group: str, position: int, group_stage_results: pd.DataFrame) -> str:
    return group_stage_results.group_results.loc[group].iloc[position-1].name

def get_knockout_games(results: GroupStageResult):
    def get_team_name(group: str, position: int):
        return results.group_results.loc[group].iloc[position - 1].name


    qualified = tuple(sorted(results.third_places.iloc[:4].index.get_level_values(0).tolist())) # top 4 third places
    third_place_enemies = third_places_advance_dict[qualified]

    return [
        (get_team_name("B", position=1), get_team_name(third_place_enemies[0], position=3)),
        (get_team_name("A", position=1), get_team_name("C", position=2)),
        (get_team_name("F", position=1), get_team_name(third_place_enemies[3], position=3)),
        (get_team_name("D", position=2), get_team_name("E", position=2)),
        (get_team_name("E", position=1), get_team_name(third_place_enemies[2], position=3)),
        (get_team_name("D", position=1), get_team_name("F", position=2)),
        (get_team_name("C", position=1), get_team_name(third_place_enemies[1], position=3)),
        (get_team_name("A", position=2), get_team_name("B", position=2)),
    ]