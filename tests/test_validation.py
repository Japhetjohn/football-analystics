import pytest
from app.validation.engine import ValidationEngine
from app.schemas.contracts import TeamStats

def test_validation_rejects_negative_stats():
    engine = ValidationEngine()
    stats = TeamStats(
        fixture_id=1,
        team_id=1,
        provider="test",
        stats={"goals": -1}
    )
    assert engine.validate_team_stats(stats) is False

def test_validation_accepts_valid_stats():
    engine = ValidationEngine()
    stats = TeamStats(
        fixture_id=1,
        team_id=1,
        provider="test",
        stats={"goals": 2}
    )
    assert engine.validate_team_stats(stats) is True
