import numpy as np
from app.statistics.engine import DixonColesEngine

def test_engine_fit_predict():
    engine = DixonColesEngine()
    engine.fit([{'home_team': 'A', 'away_team': 'B', 'home_goals': 1, 'away_goals': 1}])
    matrix = engine.predict('A', 'B')
    
    assert matrix.shape == (10, 10)
    assert np.isclose(matrix[1, 1], 0.1353, atol=1e-3)
