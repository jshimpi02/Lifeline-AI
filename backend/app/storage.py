from app.models import IncidentEvent, IncidentCluster

events: dict[str, IncidentEvent] = {}
clusters: dict[str, IncidentCluster] = {}
cluster_events: dict[str, list[str]] = {}

agent_logs = []