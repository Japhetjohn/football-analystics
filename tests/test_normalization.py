import pytest
from app.normalization.engine import NormalizationEngine

def test_generate_dqs():
    engine = NormalizationEngine()
    score = engine.generate_data_quality_score(3, 4)
    assert score == 75.0

def test_generate_dqs_zero_providers():
    engine = NormalizationEngine()
    score = engine.generate_data_quality_score(0, 0)
    assert score == 0.0

def test_normalize_team_name():
    engine = NormalizationEngine()
    mapping = {"Man Utd": "Manchester United"}
    assert engine.normalize_team_name("Man Utd", mapping) == "Manchester United"
    assert engine.normalize_team_name("Arsenal", mapping) == "Arsenal"
