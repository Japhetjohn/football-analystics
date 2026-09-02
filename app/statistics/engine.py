import numpy as np
from typing import List, Tuple, Dict

class DixonColesEngine:
    def __init__(self):
        self.params = {}
        
    def fit(self, matches: List[Dict]) -> None:
        """
        Calibrates the Poisson rates using historical matches.
        matches: List of dicts with 'home_team', 'away_team', 'home_goals', 'away_goals', 'weight'
        """
        # Todo: Implementation of Maximum Likelihood Estimation for Poisson parameters
        self.params = {"fitted": True}
        
    def predict(self, home_team: str, away_team: str) -> np.ndarray:
        """
        Returns a scoreline probability matrix P(home, away).
        Dimensions are typically (Max Goals) x (Max Goals), e.g. 10x10.
        """
        if not self.params:
            raise ValueError("Model must be fitted before predicting.")
        
        matrix = np.zeros((10, 10))
        # Hardcoded dummy probability for 1-1 draw placeholder
        matrix[1, 1] = 0.12 
        matrix[2, 1] = 0.08
        matrix[0, 0] = 0.05
        return matrix
