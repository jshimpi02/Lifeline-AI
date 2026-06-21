import json
from pathlib import Path
from app.embeddings import embed, cosine_similarity


DATA_PATH = Path("data/historical_disasters.json")


def load_historical_disasters():
    if not DATA_PATH.exists():
        return []

    with open(DATA_PATH, "r") as file:
        return json.load(file)


def find_similar_history(cluster):
    disasters = load_historical_disasters()

    if not disasters:
        return None

    cluster_text = f"{cluster.event_type} {cluster.summary}"

    best_match = None
    best_score = 0.0

    for disaster in disasters:
        disaster_text = (
            f"{disaster['event_type']} "
            f"{disaster['summary']} "
            f"{' '.join(disaster.get('insights', []))}"
        )

        score = cosine_similarity(
            embed(cluster_text),
            embed(disaster_text)
        )

        if score > best_score:
            best_score = score
            best_match = disaster

    if not best_match:
        return None
    if best_score < 0.25:
        return None

    return {
        "historical_event": best_match,
        "similarity_score": round(best_score, 3),
        "memory_insight": (
            f"This incident resembles {best_match['title']}. "
            f"Suggested action: {best_match['recommended_action']}"
        )
    }