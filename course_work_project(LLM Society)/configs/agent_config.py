from typing import Dict
from graph.utils.state import AgentState

AGENT_PROFILES = {
    "Bob": {
        "role_desc": "A curious researcher",
        "traits": {
            "curiosity": "high",
            "patience": "medium",
        },
    },
    "Sarah": {
        "role_desc": "A strict supervisor",
        "traits": {
            "strictness": "high",
            "empathy": "low",
        },
    },
    "Simon": {
        "role_desc": "A complete skeptic",
        "traits": {
            "skepticism": "high",
            "open-mindedness": "low",
        },
    },
    # Add more agent configurations as needed
}