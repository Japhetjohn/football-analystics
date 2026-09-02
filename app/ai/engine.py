import json
from typing import Dict, Any

class AIAnalysisEngine:
    """ Engine 11: Converts structured datasets to LLM Narrative without inventing data. """
    
    SYSTEM_PROMPT = (
        "You are a football analytics expert. You will be provided with a JSON formatted data structure containing "
        "match probabilities, team stats, form, head-to-head metrics, and data quality indicators.\n\n"
        "STRICT CONSTRAINTS:\n"
        "1. Write 3-5 sentences of natural-language explanation only.\n"
        "2. DO NOT introduce, calculate, or hallucinate any numbers or stats not explicitly present in the input JSON.\n"
        "3. Highlight discrepancies if Data Quality is low, or if the Models heavily disagree.\n"
    )

    def generate_narrative_payload(self, stats_payload: Dict[str, Any]) -> str:
        """
        In a full implementation, this triggers an LLM completion API call (e.g. OpenAI/Anthropic).
        Here, we return the composed payload string structurally.
        """
        return f"{self.SYSTEM_PROMPT}\n\nINPUT DATA:\n{json.dumps(stats_payload, indent=2)}"
