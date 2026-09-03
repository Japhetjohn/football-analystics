import numpy as np
from typing import List, Tuple, Dict

class DixonColesEngine:
    def __init__(self):
        self.params = None
        self.team_idx = {}
        
    def fit(self, matches: List[Dict]) -> None:
        """
        Calibrates the Poisson rates using historical matches.
        matches: List of dicts with 'home_team', 'away_team', 'home_goals', 'away_goals', 'weight'
        """
        from scipy.optimize import minimize
        teams = set([m['home_team'] for m in matches] + [m['away_team'] for m in matches])
        self.teams = list(teams)
        n = len(self.teams)
        self.team_idx = {t: i for i, t in enumerate(self.teams)}
        
        def neg_log_lik(params):
            attack = params[:n]
            defense = params[n:2*n]
            home_adv = params[-1]
            
            ll = 0
            for m in matches:
                h_i, a_i = self.team_idx[m['home_team']], self.team_idx[m['away_team']]
                lambda_home = np.clip(np.exp(attack[h_i] + defense[a_i] + home_adv), 1e-5, 15)
                lambda_away = np.clip(np.exp(attack[a_i] + defense[h_i]), 1e-5, 15)
                
                ll += (m['home_goals'] * np.log(lambda_home) - lambda_home)
                ll += (m['away_goals'] * np.log(lambda_away) - lambda_away)
            return -ll

        init_params = np.zeros(2 * n + 1)
        init_params[-1] = 0.20 # initial home advantage default
        res = minimize(neg_log_lik, init_params, method='L-BFGS-B')
        self.params = res.x
        self.attack = self.params[:n]
        self.defense = self.params[n:2*n]
        self.home_adv = self.params[-1]
        
    def predict(self, home_team: str, away_team: str) -> np.ndarray:
        """
        Returns a scoreline probability matrix P(home, away).
        Dimensions are typically (Max Goals) x (Max Goals), e.g. 10x10.
        """
        from scipy.stats import poisson
        if self.params is None:
            raise ValueError("Model must be fitted before predicting.")
        
        h_i, a_i = self.team_idx.get(home_team), self.team_idx.get(away_team)
        matrix = np.zeros((10, 10))
        if h_i is None or a_i is None:
            return matrix
            
        lambda_home = np.exp(self.attack[h_i] + self.defense[a_i] + self.home_adv)
        lambda_away = np.exp(self.attack[a_i] + self.defense[h_i])
        
        for i in range(10):
            for j in range(10):
                matrix[i, j] = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)
        return matrix
