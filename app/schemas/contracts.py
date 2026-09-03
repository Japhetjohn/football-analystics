from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class Fixture(BaseModel):
    id: int
    provider: str
    home_team_id: int
    away_team_id: int
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    competition_name: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    start_time: datetime
    competition_id: int
    status: str
    
    model_config = ConfigDict(from_attributes=True)

class TeamStats(BaseModel):
    fixture_id: int
    team_id: int
    provider: str
    stats: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)

class DataQualityMetrics(BaseModel):
    match_id: int
    quality_score: float # 0.0 - 100.0
    flags: List[str] = []
