import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from configs.agent_config import AGENT_PROFILES
from configs.models_config import MODEL_PROFILES
from configs.simulation_config import (
    DEBATE_TOPIC,
    VOTING_QUESTION,
    VOTING_OPTIONS,
    MODEL_USED_FOR_DEBATE,
    MODEL_USED_FOR_VOTING,
    DEBATE_ROUND_COUNT
)
from utils.time_and_dates import date_time_stamp


def _get_agent_profiles(personas: Optional[List[Dict[str, Any]]]):
    
    # personas intended to come from rag
    if personas:
        profiles: List[Tuple[str, Dict[str, Any]]] = []
        for persona in personas:
            name = persona.get("name", "Unknown")
            profiles.append(
                (
                    name,
                    {
                        "role_desc": persona.get("role_desc", "N/A"),
                        "keypoints": persona.get("keypoints", []),
                    },
                )
            )
        return profiles
    # personas from static config(file)
    return list(AGENT_PROFILES.items())

def format_simulation_config() -> str:
    """Format simulation configuration section."""
    lines = [
        "=" * 80,
        "SIMULATION CONFIGURATION",
        "=" * 80,
        "",
        f"Debate Topic: {DEBATE_TOPIC}",
        f"Debate Round Count: {DEBATE_ROUND_COUNT}",
        "",
        "VOTING CONFIGURATION:",
        f"  Question: {VOTING_QUESTION}",
        f"  Options: {', '.join(VOTING_OPTIONS)}",
        "",
        "MODEL ASSIGNMENTS:",
        f"  Debate Model: {MODEL_USED_FOR_DEBATE}",
        f"  Voting Model: {MODEL_USED_FOR_VOTING}",
        ""
    ]
    
    return "\n".join(lines)

def format_model_config() -> str:
    """Format model configuration section."""
    lines = [
        "=" * 80,
        "MODEL CONFIGURATIONS",
        "=" * 80,
        ""
    ]
    
    for model_name, config in MODEL_PROFILES.items():
        lines.append(f"Model: {model_name}")
        lines.append("-" * 40)
        for key, value in config.items():
            # Format the key nicely
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"  {formatted_key}: {value}")
        lines.append("")
    
    return "\n".join(lines)

def format_agent_config(personas: Optional[List[Dict[str, Any]]] = None):
    lines = [
        "=" * 80,
        "AGENT CONFIGURATIONS",
        "=" * 80,
        ""
    ]
    
    for agent_name, profile in _get_agent_profiles(personas):
        lines.append(f"Agent: {agent_name}")
        lines.append("-" * 40)
        lines.append(f"  Role: {profile.get('role_desc', 'N/A')}")
        for kp in profile.get('keypoints', []):
            lines.append(f"  - {kp}")
        
        lines.append("")
    
    return "\n".join(lines)

def format_all_configurations(personas: Optional[List[Dict[str, Any]]] = None, mode: str = "rag",
                              persona_source: Optional[str] = None) -> str:
    """Format all system configurations into a readable text format."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = [
        "=" * 80,
        "SYSTEM CONFIGURATION SNAPSHOT",
        f"Generated: {timestamp}",
        f"Mode: {mode.upper()}",
    ]
    if persona_source:
        header.append(f"Persona Source: {persona_source}  (loaded from file)")
    header.append("=" * 80)

    sections = [
        *header,
        "",
        format_simulation_config(),
        format_model_config(),
        format_agent_config(personas),
        "=" * 80,
        "END OF CONFIGURATION",
        "=" * 80
    ]
    
    return "\n".join(sections)

def save_configuration_snapshot(subsession_path, personas: Optional[List[Dict[str, Any]]] = None,
                                mode: str = "rag", persona_source: Optional[str] = None):
    """
    Save current system configuration to a timestamped file in the subsession folder.

    Args:
        subsession_path: Path to the subsession folder where config should be saved
        personas: Optional personas produced by the pipeline. When provided,
                  these are written to the agent section.
        mode: Simulation mode ("rag" or "baseline"). Written to the snapshot header.
        persona_source: Path to a persona file if personas were loaded from disk, else None.

    Returns:
        str: Path to the saved configuration file
    """
    current_time_stamp = date_time_stamp()

    filepath = os.path.join(subsession_path, f"configuration_{current_time_stamp}.txt")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(format_all_configurations(personas=personas, mode=mode, persona_source=persona_source))

    return filepath