from app.schemas.contracts import DataQualityMetrics
from typing import Dict, Any

class NormalizationEngine:
    def generate_data_quality_score(self, provider_agreements: int, total_providers: int) -> float:
        if total_providers == 0:
            return 0.0
        return (provider_agreements / total_providers) * 100.0

    def normalize_team_name(self, raw_name: str, mapping_dict: Dict[str, str]) -> str:
        # Falls back to original name if not in mapping logic
        return mapping_dict.get(raw_name, raw_name)
