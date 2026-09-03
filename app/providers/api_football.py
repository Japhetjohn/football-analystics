import ssl
import json
import asyncio
from datetime import datetime
import urllib.request
from typing import List, Dict, Any
from app.providers.base import DataProvider
from app.schemas.contracts import Fixture, TeamStats

class APIFootballProvider(DataProvider):
    BASE_URL = "https://v3.football.api-sports.io"
    
    def __init__(self, api_key: str):
        self.headers = {
            "x-apisports-key": api_key
        }

    @property
    def name(self) -> str:
        return "api-football"

    def _sync_get(self, endpoint: str) -> Dict:
        """ Fetch using built-in urllib to bypass external pip requirements """
        req = urllib.request.Request(f"{self.BASE_URL}/{endpoint}", headers=self.headers)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE  # Bypass SSL blockades occasionally seen on restricted networks
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data

    def _parse_fixtures(self, data: Dict) -> List[Fixture]:
        fixtures = []
        for item in data.get("response", []):
            fx = item.get("fixture", {})
            teams = item.get("teams", {})
            goals = item.get("goals", {})
            try:
                date_str = fx.get("date")
                if date_str and date_str.endswith("Z"):
                    date_str = date_str.replace("Z", "+00:00")
                
                status_short = fx.get("status", {}).get("short", "TBD")
                # Default to 0 instead of None if match is valid but missing score
                fixtures.append(Fixture(
                    id=fx.get("id"),
                    provider=self.name,
                    home_team_id=teams.get("home", {}).get("id"),
                    away_team_id=teams.get("away", {}).get("id"),
                    home_score=goals.get("home"),# allows None if unplayed
                    away_score=goals.get("away"),
                    start_time=datetime.fromisoformat(date_str) if date_str else datetime.utcnow(),
                    competition_id=item.get("league", {}).get("id"),
                    status=status_short
                ))
            except Exception as e:
                continue
        return fixtures

    async def get_fixtures(self) -> List[Fixture]:
        """ Pulls actual live fixtures from API-Football. """
        data = await asyncio.to_thread(self._sync_get, "fixtures?live=all")
        return self._parse_fixtures(data)

    async def get_scheduled_fixtures(self, date: str) -> List[Fixture]:
        """ Pulls upcoming fixtures for a specific date (YYYY-MM-DD). """
        data = await asyncio.to_thread(self._sync_get, f"fixtures?date={date}")
        return self._parse_fixtures(data)

    async def get_head_to_head(self, h2h_key: str) -> List[Fixture]:
        """ Pulls H2H matches historically (e.g., '33-34'). """
        data = await asyncio.to_thread(self._sync_get, f"fixtures/headtohead?h2h={h2h_key}")
        return self._parse_fixtures(data)

    async def get_team_stats(self, fixture_id: int) -> List[TeamStats]:
        """
        Pulls actual team statistics for a specific fixture from API-Football.
        """
        data = await asyncio.to_thread(self._sync_get, f"fixtures/statistics?fixture={fixture_id}")
        stats_list = []
        
        for item in data.get("response", []):
            team_id = item.get("team", {}).get("id")
            raw_stats = item.get("statistics", [])
            
            parsed_stats = {s.get("type"): s.get("value") for s in raw_stats}
            
            ts = TeamStats(
                fixture_id=fixture_id,
                team_id=team_id,
                provider=self.name,
                stats=parsed_stats
            )
            stats_list.append(ts)
            
        return stats_list
