from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
from difflib import SequenceMatcher
from app.embeddings import embed, cosine_similarity
from app.models import IncidentEvent, IncidentCluster


COMPATIBLE_TYPES = {
    "flood": ["flood", "rescue", "medical_rescue", "road_block"],
    "rescue": ["rescue", "medical_rescue", "flood"],
    "medical_rescue": ["medical_rescue", "rescue", "flood"],
    "road_block": ["road_block", "flood"],
    "power_outage": ["power_outage"],
}


def text_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def semantic_similarity(a: str, b: str) -> float:
    emb1 = embed(a)
    emb2 = embed(b)

    return cosine_similarity(emb1, emb2)

def distance_km(lat1, lng1, lat2, lng2) -> float:
    if None in [lat1, lng1, lat2, lng2]:
        return 999

    r = 6371
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)

    x = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 2 * r * atan2(sqrt(x), sqrt(1 - x))


def location_score(event: IncidentEvent, cluster: IncidentCluster) -> float:
    d = distance_km(event.location.lat, event.location.lng, cluster.lat, cluster.lng)

    if d <= 0.5:
        return 1.0
    if d <= 2:
        return 0.8
    if d <= 5:
        return 0.5
    return 0.0


def time_score(event_time: datetime, cluster_time: datetime) -> float:
    hours = abs((event_time - cluster_time).total_seconds()) / 3600

    if hours <= 1:
        return 1.0
    if hours <= 3:
        return 0.8
    if hours <= 6:
        return 0.5
    return 0.0


def type_score(event_type: str, cluster_type: str) -> float:
    if event_type == cluster_type:
        return 1.0

    compatible = COMPATIBLE_TYPES.get(cluster_type, [])
    return 0.7 if event_type in compatible else 0.0


def fusion_score(event: IncidentEvent, cluster: IncidentCluster) -> float:
    semantic = cosine_similarity(
        embed(event.raw_text),
        embed(cluster.summary)
    )

    loc = location_score(event, cluster)
    time = time_score(event.timestamp, cluster.last_updated)
    typ = type_score(event.event_type, cluster.event_type)

    return round(
        0.45 * semantic +
        0.25 * loc +
        0.20 * time +
        0.10 * typ,
        3
    )

def fusion_breakdown(event, cluster):
    semantic = cosine_similarity(
        embed(event.raw_text),
        embed(cluster.summary)
    )

    loc = location_score(event, cluster)
    time = time_score(event.timestamp, cluster.last_updated)
    typ = type_score(event.event_type, cluster.event_type)

    total = (
        0.45 * semantic +
        0.25 * loc +
        0.20 * time +
        0.10 * typ
    )

    return {
        "semantic_similarity": round(semantic, 3),
        "location_score": round(loc, 3),
        "time_score": round(time, 3),
        "type_score": round(typ, 3),
        "fusion_score": round(total, 3)
    }

    return round(
        0.45 * semantic +
        0.25 * loc +
        0.20 * time +
        0.10 * typ,
        3
    )