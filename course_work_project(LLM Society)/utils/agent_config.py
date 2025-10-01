from typing import Dict
from graph.utils.state import AgentProfile

AGENT_PROFILES: Dict[str, AgentProfile] = {
    "agent_1": {
        "role_desc": "A curious researcher",
        "traits": {
            "curiosity": "high",
            "patience": "medium",
        },
    },
    "agent_2": {
        "role_desc": "A strict supervisor",
        "traits": {
            "strictness": "high",
            "empathy": "low",
        },
    },
    # Add more agents as needed
}