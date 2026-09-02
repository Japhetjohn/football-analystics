from abc import ABC, abstractmethod
from typing import List
from app.schemas.contracts import Fixture, TeamStats

class DataProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    async def get_fixtures(self) -> List[Fixture]:
        pass
        
    @abstractmethod
    async def get_team_stats(self, fixture_id: int) -> List[TeamStats]:
        pass
