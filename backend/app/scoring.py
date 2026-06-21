from app.models import IncidentEvent

MEDICAL_NEEDS = {"oxygen", "insulin", "dialysis", "ambulance", "medicine"}
VULNERABLE_WORDS = {"elderly", "grandmother", "grandfather", "child", "baby", "nursing home", "disabled"}


def calculate_priority(events: list[IncidentEvent]) -> int:
    max_urgency = max(e.urgency for e in events)
    people = sum(e.people_affected for e in events)

    all_needs = set()
    all_text = " ".join(e.raw_text.lower() for e in events)
    sources = set(e.source for e in events)

    for event in events:
        all_needs.update(n.lower() for n in event.needs)

    score = max_urgency * 10

    if all_needs.intersection(MEDICAL_NEEDS):
        score += 15

    if any(word in all_text for word in VULNERABLE_WORDS):
        score += 10

    if people >= 10:
        score += 10
    elif people >= 3:
        score += 5

    if len(sources) >= 2:
        score += 5

    return min(score, 100)


def severity_from_priority(priority: int) -> int:
    if priority >= 90:
        return 10
    if priority >= 75:
        return 8
    if priority >= 50:
        return 6
    return 4


def recommended_action(priority: int, event_type: str) -> str:
    if priority >= 90:
        return "Immediate dispatch required"

    if event_type in ["medical_rescue", "rescue"]:
        return "Dispatch rescue/medical team"

    if event_type == "flood":
        return "Monitor flood cluster and prepare evacuation support"

    if event_type == "road_block":
        return "Send field unit to verify road access"

    if event_type == "power_outage":
        return "Notify utility response team"

    return "Review incident"