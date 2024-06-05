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
            raise FileNotFoundError("Model not found, please train the model first (refer to readme, or run main.py with --train)")

    def sample_goals(self, market_value_distance: float) -> int:
        """Samples the number of goals a team scores based on the market value distance between the two teams

        Args:
            market_value_distance (float): market value distance between the two teams

        Returns:
            int: number of goals scored by the team
        """
        expected_goals = self.model.predict([[market_value_distance]])[0]
        return np.random.poisson(expected_goals)
