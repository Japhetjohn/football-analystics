import numpy as np
from typing import Dict, Any
import xgboost as xgb

class MLEngine:
    """ Engine 8: Boosted Trees """
    def __init__(self, model_type: str = "xgboost"):
        self.model_type = model_type
        self.model = xgb.XGBClassifier(
            objective="multi:softprob", 
            num_class=3,
            eval_metric="mlogloss", 
        )
        self.is_trained = False

    def fit(self, features: np.ndarray, labels: np.ndarray) -> None:
        """
        Fits XGBoost on generated feature matrix (Form, H2H, etc.)
        """
        self.model.fit(features, labels)
        self.is_trained = True

    def predict_proba(self, match_features: Dict[str, Any]) -> np.ndarray:
        """
        Returns outcome probabilities [Home, Draw, Away].
        """
        if not self.is_trained:
            raise ValueError("ML model not trained. Call fit() first.")
            
        # Convert dict to array preserving expected order
        # Just a generic pipeline wrapper
        f_vector = np.array(list(match_features.values())).reshape(1, -1)
        preds = self.model.predict_proba(f_vector)
        return preds[0]
