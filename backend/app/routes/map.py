from fastapi import APIRouter
from app.storage import events, clusters

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/clusters")
def map_clusters():
    result = []

    for cluster in clusters.values():
        try:
            result.append({
                "cluster_id": getattr(cluster, "cluster_id", None),
                "lat": getattr(cluster, "lat", None),
                "lng": getattr(cluster, "lng", None),
                "radius": 200 + (getattr(cluster, "reports_count", 1) * 80),
                "priority_score": getattr(cluster, "priority_score", 0),
                "severity": getattr(cluster, "severity", 0),
                "reports_count": getattr(cluster, "reports_count", 1),
                "summary": getattr(cluster, "summary", ""),
                "event_type": getattr(cluster, "event_type", "other"),
                "confidence": getattr(cluster, "confidence", 0),
                "recommended_action": getattr(cluster, "recommended_action", "Review incident"),
            })
        except Exception as e:
            print("map_clusters skipped bad cluster:", e)

    return result


@router.get("/events")
def map_events():
    result = []

    for event in events.values():
        try:
            location = getattr(event, "location", None)

            result.append({
                "event_id": getattr(event, "id", None),
                "lat": getattr(location, "lat", None) if location else None,
                "lng": getattr(location, "lng", None) if location else None,
                "raw_text": getattr(event, "raw_text", ""),
                "source": getattr(event, "source", "field"),
                "event_type": getattr(event, "event_type", "other"),
                "urgency": getattr(event, "urgency", 0),
                "confidence": getattr(event, "confidence", 0),
            })
        except Exception as e:
            print("map_events skipped bad event:", e)

    return result