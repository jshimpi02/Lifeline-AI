from app.historical_memory import find_similar_history


class MemoryAgent:
    def retrieve_memory(self, cluster):
        return find_similar_history(cluster)