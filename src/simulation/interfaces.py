from dataclasses import dataclass

import pandas as pd


@dataclass
class GroupStageResult:
    """Dataclass to hold the results of the group stage simulation

        Attributes:

        qualified_top_two (pd.DataFrame): DataFrame with the top two teams from each group
        qualified_third (pd.DataFrame): DataFrame with the top four third placed teams
    """
    group_results: pd.DataFrame
    third_places: pd.DataFrame
