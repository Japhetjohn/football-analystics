import numpy as np

class EvaluationEngine:
    """ Engine 10: Backtesting """
    @staticmethod
    def brier_score(predicted_probs: np.ndarray, actual_outcome: int) -> float:
        actual = np.zeros(len(predicted_probs))
        actual[actual_outcome] = 1.0
        return np.sum((predicted_probs - actual) ** 2)

    @staticmethod
    def log_loss(predicted_probs: np.ndarray, actual_outcome: int) -> float:
        prob = predicted_probs[actual_outcome]
        prob = np.clip(prob, 1e-15, 1 - 1e-15)
        return float(-np.log(prob))
        
    def walk_forward_backtest(self, matches: list, model, window_size: int):
        results = []
        for i in range(window_size, len(matches)):
            train_set = matches[:i]
            test_match = matches[i]
            
            model.fit(train_set)
            probs = model.predict(test_match['home'], test_match['away'])
            
            actual_outcome = test_match.get('outcome', 1) 
            prob_array = np.array([0.4, 0.3, 0.3]) # mock
            
            results.append({
                "match_id": test_match['id'],
                "brier": self.brier_score(prob_array, actual_outcome),
                "logloss": self.log_loss(prob_array, actual_outcome)
            })
        return results

    def score_vs_baseline(self, ensemble_brier: float, baseline_brier: float) -> str:
        """
        Compares the ensemble engine's performance against historical bookmaker odds Brier scores.
        """
        improvement = baseline_brier - ensemble_brier
        if improvement > 0:
            return f"Ensemble beats baseline by {improvement:.4f} Brier units."
        return f"Ensemble underperforms baseline by {abs(improvement):.4f} Brier units."
