import numpy as np
from app.evaluation.engine import EvaluationEngine

def test_brier_score():
    engine = EvaluationEngine()
    probs = np.array([0.5, 0.3, 0.2])
    # Outcome 0 (Home Win)
    # Brier: (0.5-1)^2 + (0.3-0)^2 + (0.2-0)^2 = 0.25 + 0.09 + 0.04 = 0.38
    brier = engine.brier_score(probs, 0)
    assert np.isclose(brier, 0.38)
    
def test_log_loss():
    engine = EvaluationEngine()
    probs = np.array([0.5, 0.3, 0.2])
    ll = engine.log_loss(probs, 0)
    assert np.isclose(ll, -np.log(0.5))
