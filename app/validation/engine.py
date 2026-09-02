from app.schemas.contracts import Fixture, TeamStats

class ValidationEngine:
    def validate_team_stats(self, stats: TeamStats) -> bool:
        # Check plausibility: negative stats not allowed
        for key, value in stats.stats.items():
            if isinstance(value, (int, float)) and value < 0:
                return False
        return True
