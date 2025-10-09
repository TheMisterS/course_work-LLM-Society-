import os
from datetime import datetime
from configs.agent_config import AGENT_PROFILES
from configs.models_config import MODEL_PROFILES


def format_all_configurations() -> str:
    """Format all system configurations into a readable text format."""
    timestamp = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    
    output = [
        "=" * 80,
        "SYSTEM CONFIGURATION SNAPSHOT",
        f"Generated: {timestamp}",
        "",
        "=" * 60,
        str(MODEL_PROFILES),
        "",
        "=" * 60,
        "AGENT CONFIGURATIONS",
        "=" * 60,
        str(AGENT_PROFILES),
        ""
    ]
    
    return "\n".join(output)


def save_configuration_snapshot(base_dir="results"):
    """
    Save current system configuration to a timestamped file.
    
    Args:
        base_dir: Base directory for results (default: "results")
    
    Returns:
        Path to the saved configuration file
    """
    now = datetime.now()
    session_dir = os.path.join(base_dir, f"session_{now:%Y.%m.%d}")
    os.makedirs(session_dir, exist_ok=True)
    
    filepath = os.path.join(session_dir, f"configuration_{now:%Y.%m.%d_%H.%M.%S}.txt")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(format_all_configurations())
    
    return filepath