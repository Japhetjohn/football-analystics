from app.providers.base import DataProvider
from app.schemas.contracts import Fixture, TeamStats
from typing import List

class StatsBombProvider(DataProvider):
    @property
    def name(self) -> str:
        return "statsbomb"
        
    async def get_fixtures(self) -> List[Fixture]:
        # Reads from locally cloned StatsBomb open data json files
        return []

    async def get_team_stats(self, fixture_id: int) -> List[TeamStats]:
        # Aggregates shot maps to team xG stats from open data json
        return []
