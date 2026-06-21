from uuid import uuid4

from app.models import IncidentCluster
from app.storage import events, clusters, cluster_events
from app.fusion import fusion_score
from app.scoring import calculate_priority, severity_from_priority, recommended_action
from app.confidence import calculate_cluster_confidence

FUSION_THRESHOLD = 0.75


class FusionAgent:
    def submit_event(self, event):
        if event.id in events:
            return {
                "status": "duplicate_ignored",
                "event_id": event.id,
                "message": "Event already exists"
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

            updated_cluster = self.rebuild_cluster(cluster_id)
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
            "fusion_score": 1.0,
            "fusion_reason": "Created new cluster because no matching cluster existed",
            "cluster": new_cluster
        }

    def rebuild_cluster(self, cluster_id):
        ids = cluster_events[cluster_id]
        cluster_event_list = [events[eid] for eid in ids]

        priority = calculate_priority(cluster_event_list)
        severity = severity_from_priority(priority)
        cluster_confidence = calculate_cluster_confidence(cluster_event_list)

        first_event_with_location = next(
            (
                e for e in cluster_event_list
                if e.location.lat is not None and e.location.lng is not None
            ),
            None
        )

        lat = first_event_with_location.location.lat if first_event_with_location else None
        lng = first_event_with_location.location.lng if first_event_with_location else None

        event_types = [e.event_type for e in cluster_event_list]
        event_type = max(set(event_types), key=event_types.count)

        summary = self.generate_cluster_summary(cluster_event_list)

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

    def generate_cluster_summary(self, cluster_event_list):
        event_type = cluster_event_list[0].event_type
        location = cluster_event_list[0].location.text
        count = len(cluster_event_list)
        total_people = sum(e.people_affected for e in cluster_event_list)

        return (
            f"{count} reports related to {event_type.replace('_', ' ')} "
            f"near {location}. Estimated {total_people} people affected."
        )