from app.agents.extraction_agent import ExtractionAgent
from app.agents.fusion_agent import FusionAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.prioritization_agent import PrioritizationAgent
from app.storage import clusters
from app.asi_client import asi_one_json


class CoordinatorAgent:
    def __init__(self):
        self.extraction_agent = ExtractionAgent()
        self.fusion_agent = FusionAgent()
        self.memory_agent = MemoryAgent()
        self.prioritization_agent = PrioritizationAgent()

    def process_report(self, raw_text: str, source: str = "web"):
        event = self.extraction_agent.extract_event(raw_text, source)
        fusion_result = self.fusion_agent.submit_event(event)

        cluster_id = fusion_result.get("cluster_id")
        cluster = clusters.get(cluster_id)

        memory_result = None
        if cluster:
            memory_result = self.memory_agent.retrieve_memory(cluster)

        ranked_clusters = self.prioritization_agent.rank_clusters()

        return {
            "agent_trace": [
                "ASI:One Coordinator",
                "ExtractionAgent",
                "FusionAgent",
                "MemoryAgent",
                "PrioritizationAgent",
                "ASI:One Recommendation"
            ],
            "raw_text": raw_text,
            "extracted_event": event,
            "fusion_result": fusion_result,
            "memory_result": memory_result,
            "ranked_clusters": ranked_clusters,
            "final_recommendation": self.generate_recommendation(
                fusion_result,
                memory_result,
                ranked_clusters
            )
        }

    def generate_recommendation(self, fusion_result, memory_result, ranked_clusters):
        if not ranked_clusters:
            return {
                "recommendation": "No active incidents require action.",
                "reason": "No active clusters found.",
                "next_steps": []
            }

        top = ranked_clusters[0]

        prompt = f"""
You are ASI:One, the coordinator brain for Lifeline AI, an emergency response intelligence platform.

Generate a responder recommendation using this incident state.

Top ranked incident:
{top}

Fusion result:
{fusion_result}

Historical memory:
{memory_result}

Return ONLY valid JSON with this exact schema:
{{
  "recommendation": "clear responder action",
  "reason": "why this is the highest priority",
  "next_steps": ["step 1", "step 2", "step 3"]
}}
"""

        try:
            return asi_one_json(prompt)
        except Exception as e:
            return {
                "recommendation": top["recommended_action"],
                "reason": f"ASI:One fallback used because: {str(e)}",
                "next_steps": [
                    "Review cluster details",
                    "Dispatch appropriate response unit",
                    "Continue monitoring incoming reports"
                ]
            }