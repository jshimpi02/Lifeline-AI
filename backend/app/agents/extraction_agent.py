from datetime import datetime
from uuid import uuid4
import random
from app.models import IncidentEvent, Location


class ExtractionAgent:
    def extract_event(self, raw_text: str, source: str = "web") -> IncidentEvent:
        text = raw_text.lower()

        event_type = "other"
        needs = []
        urgency = 4

        if "flood" in text or "water" in text:
            event_type = "flood"
            urgency = 7

        if "rescue" in text or "trapped" in text or "stranded" in text:
            event_type = "rescue"
            needs.append("rescue")
            urgency = max(urgency, 8)

        if "oxygen" in text or "insulin" in text or "medical" in text:
            event_type = "medical_rescue"
            needs.append("medical")
            urgency = max(urgency, 9)

        location_text = "Unknown"
        lat = None
        lng = None

        if "walmart" in text:
            location_text = "Market Street"
            lat = 37.7749 + random.uniform(-0.01, 0.01)
            lng = -122.4194 + random.uniform(-0.01, 0.01)

        elif "downtown" in text:
            location_text = "Downtown San Francisco"
            lat = 37.7749 + random.uniform(-0.01, 0.01)
            lng = -122.4194 + random.uniform(-0.01, 0.01)

        elif "nursing home" in text:
            location_text = "Pine Street Nursing Home"
            lat = 37.7849 + random.uniform(-0.01, 0.01)
            lng = -122.4094 + random.uniform(-0.01, 0.01)

        return IncidentEvent(
            id=f"evt_{str(uuid4())[:8]}",
            raw_text=raw_text,
            source=source,
            event_type=event_type,
            location=Location(
                text=location_text,
                lat=lat,
                lng=lng
            ),
            urgency=urgency,
            needs=needs,
            people_affected=1,
            timestamp=datetime.utcnow(),
            confidence=0.85
        )