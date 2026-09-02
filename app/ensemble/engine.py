import numpy as np

class EnsembleEngine:
    """ Engine 9: Combinator Logic """
    def __init__(self, stat_weight: float = 0.5, ml_weight: float = 0.5):
        self.stat_weight = stat_weight
        self.ml_weight = ml_weight

    def predict(self, stat_probs: np.ndarray, ml_probs: np.ndarray) -> np.ndarray:
        """
        Linearly ensembles the Dixon-Coles and XGBoost probabilities.
        """
        if len(stat_probs) != len(ml_probs):
            raise ValueError("Probability arrays must align.")
            
        combined = (stat_probs * self.stat_weight) + (ml_probs * self.ml_weight)
        
        # Normalize sum to 1 strictly
        return combined / np.sum(combined)
