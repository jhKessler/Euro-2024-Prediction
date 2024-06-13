from collections import defaultdict
import pandas as pd
from ..model.goal_sampler import GoalSampler
from .interfaces import GroupStageResult

goal_sampler = GoalSampler()

from collections import defaultdict
import pandas as pd


def get_ties(
    leaderboard: pd.DataFrame, relevant_parameters: list[str]
) -> tuple[list[pd.DataFrame], pd.DataFrame]:
    """_summary_

    Args:
        leaderboard (pd.DataFrame): _description_
        relevant_parameters (list[str]): _description_

    Returns:
        tuple[list[pd.DataFrame], pd.DataFrame]: tuple with list of all tied groups and all non tied teams
    """
    ties_filt = leaderboard.duplicated(relevant_parameters, keep=False)
    ties = leaderboard[ties_filt]
    ties.sort_values(
        relevant_parameters,
        ascending=[False for _ in relevant_parameters],
        inplace=True,
    )
    if ties.empty:
        return [], leaderboard
    # put into groups that are tied with each other
    groups = []
    for _, group in ties.groupby(relevant_parameters):
        groups.append(group)
    return (groups, leaderboard[~ties_filt])


def assign_points(game: pd.Series) -> tuple[int, int]:
    if game["team1_goals"] > game["team2_goals"]:
        return 3, 0
    elif game["team1_goals"] < game["team2_goals"]:
        return 0, 3
    else:
        return 1, 1


def build_leaderboard(games: pd.DataFrame) -> pd.DataFrame:
    points = defaultdict(int)
    goals = defaultdict(int)
    goals_conceded = defaultdict(int)

    for _, game in games.iterrows():
        team1_points, team2_points = assign_points(game)
        points[game["team1"]] += team1_points
        points[game["team2"]] += team2_points

        goals[game["team1"]] += game["team1_goals"]
        goals[game["team2"]] += game["team2_goals"]

        goals_conceded[game["team1"]] += game["team2_goals"]
        goals_conceded[game["team2"]] += game["team1_goals"]

    df = pd.DataFrame(
        {"points": points, "goals": goals, "goals_conceded": goals_conceded}
    )
    df["goal_difference"] = df["goals"] - df["goals_conceded"]
    return df


def reorder(team_games: pd.DataFrame, leaderboard: pd.DataFrame) -> list[str]:
    if len(leaderboard) <= 1:
        raise ValueError(
            "There is only one team in the group, no need to reorder, this should not happen"
        )
    between_them_leaderboard = build_leaderboard(team_games)
    between_them_leaderboard.sort_values(
        ["points", "goal_difference", "goals"],
        ascending=[False, False, False],
        inplace=True,
    )
    placements = [None for _ in between_them_leaderboard.index]
    tied_groups, non_tied_teams = get_ties(
        between_them_leaderboard, ["points", "goal_difference", "goals"]
    )
    # teams are still tied, so we need to check the whole leaderboard
    if len(tied_groups) == 1 and non_tied_teams.empty:
        result = []
        for team in leaderboard.index:
            if team in tied_groups[0].index:
                result.append(team)
        return result

    # teams that are not tied, stay at their position
    for team, index in zip(
        non_tied_teams.index,
        between_them_leaderboard.index.get_indexer(non_tied_teams.index),
    ):
        placements[index] = team

    if None not in placements:
        return placements

    # recursively reorder the tied groups
    for tied_group in tied_groups:
        previous_indices = between_them_leaderboard.index.get_indexer(tied_group.index)
        matches_between_them = team_games[
            (team_games["team1"].isin(tied_group.index))
            & (team_games["team2"].isin(tied_group.index))
        ]
        new_order = reorder(matches_between_them, leaderboard)
        for team, index in zip(new_order, previous_indices):
            placements[index] = team

    if None in placements:
        raise ValueError(
            "There are still teams that are tied"
        )  # fifa has some weird rules for this, if this happens, i will just randomly assign the teams

    return placements


def calculate_leaderboard_order(group_games: pd.DataFrame) -> pd.DataFrame:
    group_results = build_leaderboard(group_games)
    group_results.sort_values(
        ["points", "goal_difference", "goals"],
        ascending=[False, False, False],
        inplace=True,
    )
    # check if there are any ties
    tied_groups, non_tied_teams = get_ties(group_results, ["points"])
    placements = [None for _ in group_results.index]  # this will be our final order

    # non ties teams stay at their position
    for team, index in zip(
        non_tied_teams.index, group_results.index.get_indexer(non_tied_teams.index)
    ):
        placements[index] = team

    # apply uefa logic to the ties
    for tied_group in tied_groups:
        previous_indices = group_results.index.get_indexer(tied_group.index)
        matches_between_them = group_games[
            (group_games["team1"].isin(tied_group.index))
            & (group_games["team2"].isin(tied_group.index))
        ]
        new_order = reorder(
            matches_between_them, group_results
        )  # this returns the correct order
        for team, index in zip(new_order, previous_indices):
            placements[index] = team

    return group_results.reindex(placements)


def get_group_phase_results(group_phase_games: pd.DataFrame) -> GroupStageResult:
    """
    Calculate the group stage results

    Args:
        group_phase_games (pd.DataFrame): df with columns: team1, team2, team1_goals, team2_goals

    Returns:
        GroupStageResult: _description_
    """
    # get results for each group
    group_results = group_phase_games.groupby("group").apply(
        calculate_leaderboard_order
    )
    third_places = (
        group_results.groupby(level=0)
        .apply(lambda x: x.iloc[2:3])
        .sort_values(
            by=["points", "goal_difference", "goals"], ascending=[False, False, False]
        )
        .reset_index(level=0, drop=True)
    )  # get top 4 third places
    return GroupStageResult(group_results, third_places)


def simulate_group_phase(group_phase_games: pd.DataFrame) -> GroupStageResult:
    group_phase_games["team1_goals"] = group_phase_games[
        "team1_market_value_distance"
    ].apply(goal_sampler).round()
    group_phase_games["team2_goals"] = group_phase_games[
        "team2_market_value_distance"
    ].apply(goal_sampler).round()
    return group_phase_games
    return get_group_phase_results(group_phase_games)
