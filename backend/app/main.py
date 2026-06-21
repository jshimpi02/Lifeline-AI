from fastapi import FastAPI
from uuid import uuid4

from app.models import IncidentEvent, IncidentCluster
from app.storage import events, clusters, cluster_events
from app.fusion import fusion_score, fusion_breakdown
from app.scoring import calculate_priority, severity_from_priority, recommended_action
from app.triage import is_actionable, actionability_score
from app.historical_memory import find_similar_history
from app.confidence import calculate_cluster_confidence, confidence_reasons
from app.routes.map import router as map_router
from app.agents.coordinator_agent import CoordinatorAgent
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.agents.asi_tool_orchestrator import ASIToolOrchestrator
from app.routes.map import router as map_router
from app.storage import agent_logs




app = FastAPI(title="Lifeline AI Incident Fusion Engine")
app.include_router(map_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(map_router)
FUSION_THRESHOLD = 0.75

asi_tool_orchestrator = ASIToolOrchestrator()
coordinator_agent = CoordinatorAgent()


class AgentReportRequest(BaseModel):
    raw_text: str
    source: str = "web"

@app.get("/")
def root():
    return {"message": "Lifeline AI Incident Fusion Engine running"}


@app.post("/events")
def add_event(event: IncidentEvent):
    if event.id in events:
        return {
            "status": "duplicate_ignored",
            "event_id": event.id,
            "message": "Event already exists"
        }
    if not is_actionable(event):
        return {
            "status": "quarantined",
            "event_id": event.id,
            "actionability_score": actionability_score(event),
            "message": "Event not actionable enough for fusion"
        }
    events[event.id] = event

    best_cluster = None
    best_score = 0

    for cluster in clusters.values():
        score = fusion_score(event, cluster)
        if score > best_score:
            best_score = score
            best_cluster = cluster

    if best_cluster and best_score >= FUSION_THRESHOLD:
        cluster_id = best_cluster.cluster_id

        if event.id not in cluster_events[cluster_id]:
            cluster_events[cluster_id].append(event.id)

        updated_cluster = rebuild_cluster(cluster_id)
        clusters[cluster_id] = updated_cluster

        return {
            "status": "merged",
            "cluster_id": cluster_id,
            "fusion_score": best_score,
            "cluster": updated_cluster
        }

    cluster_id = f"cluster_{str(uuid4())[:8]}"
    cluster_events[cluster_id] = [event.id]

    new_cluster = IncidentCluster(
        cluster_id=cluster_id,
        event_type=event.event_type,
        summary=event.raw_text,
        event_ids=[event.id],
        lat=event.location.lat,
        lng=event.location.lng,
        severity=event.urgency,
        priority_score=event.urgency * 10,
        confidence=event.confidence,
        reports_count=1,
        recommended_action=recommended_action(event.urgency * 10, event.event_type),
        last_updated=event.timestamp
    )

    clusters[cluster_id] = new_cluster

    return {
        "status": "created",
        "cluster_id": cluster_id,
        "fusion_score": best_score,
        "fusion_reason": "Created new cluster because no matching cluster existed",
        "cluster": new_cluster
    }


def rebuild_cluster(cluster_id: str) -> IncidentCluster:
    ids = cluster_events[cluster_id]
    cluster_event_list = [events[eid] for eid in ids]

    priority = calculate_priority(cluster_event_list)
    severity = severity_from_priority(priority)

    cluster_confidence = calculate_cluster_confidence(cluster_event_list)

    lat_values = [e.location.lat for e in cluster_event_list if e.location.lat is not None]
    lng_values = [e.location.lng for e in cluster_event_list if e.location.lng is not None]

    lat = sum(lat_values) / len(lat_values) if lat_values else None
    lng = sum(lng_values) / len(lng_values) if lng_values else None

    event_types = [e.event_type for e in cluster_event_list]
    event_type = max(set(event_types), key=event_types.count)

    summary = generate_cluster_summary(cluster_event_list)

    return IncidentCluster(
        cluster_id=cluster_id,
        event_type=event_type,
        summary=summary,
        event_ids=ids,
        lat=lat,
        lng=lng,
        severity=severity,
        priority_score=priority,
        confidence=cluster_confidence,
        reports_count=len(ids),
        recommended_action=recommended_action(priority, event_type),
        last_updated=max(e.timestamp for e in cluster_event_list)
    )


def generate_cluster_summary(cluster_event_list: list[IncidentEvent]) -> str:
    event_type = cluster_event_list[0].event_type
    location = cluster_event_list[0].location.text
    count = len(cluster_event_list)

    total_people = sum(e.people_affected for e in cluster_event_list)

    return (
        f"{count} reports related to {event_type.replace('_', ' ')} "
        f"near {location}. Estimated {total_people} people affected."
    )


@app.get("/clusters")
def get_clusters():
    return list(clusters.values())


@app.get("/clusters/{cluster_id}")
def get_cluster(cluster_id: str):
    cluster = clusters.get(cluster_id)

    if not cluster:
        return {"error": "Cluster not found"}

    related_events = [events[eid] for eid in cluster_events[cluster_id]]

    return {
        "cluster": cluster,
        "events": related_events
    }


@app.get("/clusters/{cluster_id}/explain")
def explain_cluster(cluster_id: str):
    cluster = clusters.get(cluster_id)

    if not cluster:
        return {"error": "Cluster not found"}

    related_events = [events[eid] for eid in cluster_events[cluster_id]]

    reasoning = []

    max_urgency = max(e.urgency for e in related_events)
    total_people = sum(e.people_affected for e in related_events)

    all_needs = []
    for event in related_events:
        all_needs.extend(event.needs)

    sources = set(e.source for e in related_events)

    if max_urgency >= 8:
        reasoning.append(f"High urgency detected with max urgency {max_urgency}/10")

    if total_people > 1:
        reasoning.append(f"{total_people} people potentially affected")

    if all_needs:
        reasoning.append(f"Needs detected: {list(set(all_needs))}")

    if len(sources) > 1:
        reasoning.append(f"Multiple sources confirm this cluster: {list(sources)}")

    reasoning.append(f"Priority score calculated as {cluster.priority_score}/100")
    reasoning.append(f"Recommended action: {cluster.recommended_action}")

    reasoning.extend(confidence_reasons(related_events))

    return {
        "cluster_id": cluster.cluster_id,
        "summary": cluster.summary,
        "reports_count": cluster.reports_count,
        "priority_score": cluster.priority_score,
        "severity": cluster.severity,
        "confidence": cluster.confidence,
        "recommended_action": cluster.recommended_action,
        "reasoning": reasoning
    }

@app.get("/clusters/{cluster_id}/debug")
def debug_cluster(cluster_id: str):
    cluster = clusters.get(cluster_id)

    if not cluster:
        return {"error": "Cluster not found"}

    related_events = [events[eid] for eid in cluster_events[cluster_id]]

    sources = list(set(e.source for e in related_events))
    event_types = list(set(e.event_type for e in related_events))

    max_urgency = max(e.urgency for e in related_events)
    avg_confidence = sum(e.confidence for e in related_events) / len(related_events)
    total_people = sum(e.people_affected for e in related_events)

    return {
        "cluster_id": cluster.cluster_id,
        "summary": cluster.summary,
        "reports_count": cluster.reports_count,
        "event_ids": cluster.event_ids,
        "event_types": event_types,
        "sources": sources,
        "location": {
            "lat": cluster.lat,
            "lng": cluster.lng
        },
        "scoring_debug": {
            "priority_score": cluster.priority_score,
            "severity": cluster.severity,
            "max_urgency": max_urgency,
            "total_people_affected": total_people,
            "avg_confidence": round(avg_confidence, 2)
        },
        "fusion_debug": {
            "fusion_threshold": FUSION_THRESHOLD,
            "cluster_confidence": cluster.confidence,
            "merged_reports": [
                {
                    "event_id": e.id,
                    "raw_text": e.raw_text,
                    "source": e.source,
                    "event_type": e.event_type,
                    "urgency": e.urgency,
                    "confidence": e.confidence,
                    "location_text": e.location.text
                }
                for e in related_events
            ]
        }
    }
@app.get("/clusters/{cluster_id}/similar-history")
def similar_history(cluster_id: str):
    cluster = clusters.get(cluster_id)

    if not cluster:
        return {"error": "Cluster not found"}

    result = find_similar_history(cluster)

    if not result:
        return {
            "cluster_id": cluster_id,
            "message": "No historical memory found"
        }

    return {
        "cluster_id": cluster_id,
        "cluster_summary": cluster.summary,
        "similarity_score": result["similarity_score"],
        "historical_event": result["historical_event"],
        "memory_insight": result["memory_insight"]
    }

@app.get("/clusters/{cluster_id}/fusion-debug")
def fusion_debug(cluster_id: str):

    cluster = clusters.get(cluster_id)

    if not cluster:
        return {"error": "Cluster not found"}

    related_events = [
        events[eid]
        for eid in cluster_events[cluster_id]
    ]

    if len(related_events) == 0:
        return {"error": "No events found"}

    results = []

    for event in related_events:

        breakdown = fusion_breakdown(
            event,
            cluster
        )

        results.append({
            "event_id": event.id,
            "raw_text": event.raw_text,
            **breakdown
        })

    return {
        "cluster_id": cluster_id,
        "cluster_summary": cluster.summary,
        "fusion_threshold": FUSION_THRESHOLD,
        "event_breakdowns": results
    } 

@app.get("/agent/logs")
def get_agent_logs():
    return agent_logs

@app.post("/agent/process-report")
def agent_process_report(request: AgentReportRequest):
    return coordinator_agent.process_report(
        raw_text=request.raw_text,
        source=request.source
    )

@app.post("/agent/asi-process-report")
def asi_process_report(request: AgentReportRequest):
    return asi_tool_orchestrator.process_report(
        raw_text=request.raw_text,
        source=request.source
    )


@app.post("/reset")
def reset():
    events.clear()
    clusters.clear()
    cluster_events.clear()
    return {"status": "reset"}