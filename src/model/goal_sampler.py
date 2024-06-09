import pickle
import numpy as np


class GoalSampler:
    """
    Uses the poissont distribution to sample how many goals a team shoots
    """

    def __init__(self):
        try:
            with open("data/models/linear_regression.pkl", "rb") as f:
                self.model = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                "Model not found, please train the model first (refer to readme, or run main.py with --train)"
            )

    def sample_goals(self, market_value_distance: float) -> int:
        """Samples the number of goals a team scores based on the market value distance between the two teams

        Args:
            market_value_distance (float): market value distance between the two teams

        Returns:
            int: number of goals scored by the team
        """
        expected_goals = self.model.predict([[market_value_distance]])[0]
        return np.random.poisson(expected_goals)
    
    
    def get_knockout_stage_winner(self, team1: str, team2: str, team1_market_value: float, team2_market_value: float) -> str:
        distance = (team1_market_value - team2_market_value)
        team1_goals = self.sample_goals(distance)
        team2_goals = self.sample_goals(-distance)
        if team1_goals == team2_goals:
            # lets just assume penalties are random
            return np.random.choice([team1, team2])
        return team1 if team1_goals > team2_goals else team2
    

    def __call__(self, market_value_distance: float) -> int:
        return self.sample_goals(market_value_distance)
        