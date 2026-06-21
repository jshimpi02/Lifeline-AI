from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class Location(BaseModel):
    text: str
    lat: Optional[float] = None
    lng: Optional[float] = None


class IncidentEvent(BaseModel):
    id: str
    raw_text: str
    source: Literal["voice", "web", "social", "weather", "field"]
    event_type: str
    location: Location
    urgency: int = Field(ge=1, le=10)
    needs: List[str] = []
    people_affected: int = 1
    timestamp: datetime
    confidence: float = Field(ge=0, le=1)


class IncidentCluster(BaseModel):
    cluster_id: str
    event_type: str
    summary: str
    event_ids: List[str]
    lat: Optional[float] = None
    lng: Optional[float] = None
    severity: int
    priority_score: int
    confidence: float
    reports_count: int
    recommended_action: str
    last_updated: datetime