from app.models import IncidentEvent


def calculate_cluster_confidence(events: list[IncidentEvent]) -> float:
    if not events:
        return 0.0

    avg_event_confidence = sum(e.confidence for e in events) / len(events)

    sources = set(e.source for e in events)
    source_diversity_score = min(len(sources) / 3, 1.0)

    report_count_score = min(len(events) / 5, 1.0)

    confidence = (
        0.50 * avg_event_confidence +
        0.25 * source_diversity_score +
        0.25 * report_count_score
    )

    return round(min(confidence, 1.0), 2)


def confidence_reasons(events: list[IncidentEvent]) -> list[str]:
    if not events:
        return ["No reports available"]

    reasons = []

    avg_event_confidence = sum(e.confidence for e in events) / len(events)
    sources = set(e.source for e in events)

    reasons.append(f"Average report confidence: {round(avg_event_confidence, 2)}")
    reasons.append(f"{len(events)} reports fused into this cluster")
    reasons.append(f"{len(sources)} unique source types: {list(sources)}")

    if len(events) >= 3:
        reasons.append("Multiple reports increase confidence")

    if len(sources) >= 2:
        reasons.append("Independent source diversity increases confidence")

    return reasons