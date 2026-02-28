import os
from datetime import datetime
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
from utils.time_and_dates import date_stamp, date_time_stamp

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

def format_agent_config() -> str:
    """Format agent configuration section."""
    lines = [
        "=" * 80,
        "AGENT CONFIGURATIONS",
        "=" * 80,
        ""
    ]
    
    for agent_name, profile in AGENT_PROFILES.items():
        lines.append(f"Agent: {agent_name}")
        lines.append("-" * 40)
        lines.append(f"  Role: {profile.get('role_desc', 'N/A')}")
        for trait, desc in profile.get('traits', {}).items():
            lines.append(f"  Trait - {trait}: {desc}")
        
        lines.append("")
    
    return "\n".join(lines)

def format_all_configurations() -> str:
    """Format all system configurations into a readable text format."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sections = [
        "=" * 80,
        "SYSTEM CONFIGURATION SNAPSHOT",
        f"Generated: {timestamp}",
        "=" * 80,
        "",
        format_simulation_config(),
        format_model_config(),
        format_agent_config(),
        "=" * 80,
        "END OF CONFIGURATION",
        "=" * 80
    ]
    
    return "\n".join(sections)

def save_configuration_snapshot(subsession_path):
    """
    Save current system configuration to a timestamped file in the subsession folder.
    
    Args:
        subsession_path: Path to the subsession folder where config should be saved
    
    Returns:
        str: Path to the saved configuration file
    """
    current_time_stamp = date_time_stamp()
    
    filepath = os.path.join(subsession_path, f"configuration_{current_time_stamp}.txt")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(format_all_configurations())
    
    return filepath