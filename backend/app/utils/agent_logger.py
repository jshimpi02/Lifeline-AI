from datetime import datetime
from app.storage import agent_logs

def log_agent(agent: str, action: str):
    agent_logs.insert(0, {
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
        "agent": agent,
        "action": action
    })

    agent_logs[:] = agent_logs[:100]