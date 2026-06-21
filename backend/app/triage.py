from app.models import IncidentEvent

KEYWORDS = [
    "flood", "flooding", "rescue", "help", "trapped",
    "evacuation", "fire", "medical", "oxygen", "insulin",
    "power outage", "road blocked", "stranded", "water rising"
]


def actionability_score(event: IncidentEvent) -> float:
    score = 0.0
    text = event.raw_text.lower()

    if event.location.text or (event.location.lat and event.location.lng):
        score += 0.3

    if event.urgency >= 5:
        score += 0.2

    if any(keyword in text for keyword in KEYWORDS):
        score += 0.4

    if event.confidence >= 0.7:
        score += 0.1

    return round(min(score, 1.0), 2)


def is_actionable(event: IncidentEvent) -> bool:
    return actionability_score(event) >= 0.5