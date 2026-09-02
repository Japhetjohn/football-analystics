from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    canonical_name = Column(String, unique=True, nullable=False)

class TeamNameMapping(Base):
    __tablename__ = 'team_name_mapping'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    provider = Column(String, nullable=False)
    provider_name = Column(String, nullable=False)
    
    team = relationship("Team", backref="mappings")

class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String)  # 'FINISHED', 'SCHEDULED'
    data_quality_score = Column(Float)
    
class RawProviderData(Base):
    __tablename__ = 'raw_provider_data'
    
    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
