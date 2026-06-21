from app.storage import clusters


class PrioritizationAgent:
    def rank_clusters(self):
        ranked = sorted(
            clusters.values(),
            key=lambda c: c.priority_score,
            reverse=True
        )

        return [
            {
                "cluster_id": c.cluster_id,
                "summary": c.summary,
                "priority_score": c.priority_score,
                "confidence": c.confidence,
                "recommended_action": c.recommended_action
            }
            for c in ranked
        ]