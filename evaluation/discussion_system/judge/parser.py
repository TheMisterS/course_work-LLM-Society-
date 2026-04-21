"""
State JSON parsing utilities.
"""

import json
from pathlib import Path
from typing import Optional

from models import DebateState, AgentData, Message


def parse_state_file(state_path: Path) -> DebateState:
    """
    Parse a state JSON file into a DebateState object.
    
    Args:
        state_path: Path to the state JSON file
        
    Returns:
        DebateState object with all parsed data
        
    Raises:
        FileNotFoundError: If state file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    with open(state_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Parse messages
    messages = [
        Message(
            role=msg.get("role", "agent"),
            name=msg.get("name", "Unknown"),
            content=msg.get("content", "")
        )
        for msg in data.get("messages", [])
    ]
    
    # Parse agents
    agents = {}
    for agent_name, agent_data in data.get("agents", {}).items():
        # Traits are dynamic key-value pairs
        traits = agent_data.get("traits", {})
        
        short_mem = [
            Message(
                role=msg.get("role", "agent"),
                name=msg.get("name", "Unknown"),
                content=msg.get("content", "")
            )
            for msg in agent_data.get("short_mem", [])
        ]
        
        agents[agent_name] = AgentData(
            name=agent_data.get("name", agent_name),
            role_desc=agent_data.get("role_desc", ""),
            traits=traits,
            long_mem=agent_data.get("long_mem", []),
            short_mem=short_mem,
            agent_agenda=agent_data.get("agent_agenda", {})
        )
    
    return DebateState(
        messages=messages,
        agents=agents,
        votes=data.get("votes", {}),
        voting_options=data.get("voting_options", []),
        voting_question=data.get("voting_question", ""),
        agenda=data.get("agenda", {}),
        round=data.get("round", 0),
        phase=data.get("phase", "")
    )


def find_state_file(subsession_path: Path) -> Optional[Path]:
    """
    Find the state JSON file in a subsession directory.
    
    Args:
        subsession_path: Path to subsession directory
        
    Returns:
        Path to state file if found, None otherwise
    """
    state_files = list(subsession_path.glob("state_*.json"))
    if state_files:
        return state_files[0]
    return None


def discover_subsessions(session_path: Path) -> list[Path]:
    """
    Discover all subsession directories in a session.
    
    Args:
        session_path: Path to session directory (e.g., session_2025.12.23)
        
    Returns:
        List of paths to subsession directories
    """
    subsessions = []
    for item in session_path.iterdir():
        if item.is_dir() and item.name.startswith("subsession_"):
            subsessions.append(item)
    return sorted(subsessions)


def discover_sessions(results_path: Path) -> list[Path]:
    """
    Discover all session directories in results folder.
    
    Args:
        results_path: Path to results directory
        
    Returns:
        List of paths to session directories
    """
    sessions = []
    for item in results_path.iterdir():
        if item.is_dir() and item.name.startswith("session_"):
            sessions.append(item)
    return sorted(sessions)


def get_session_name(subsession_path: Path) -> str:
    """
    Extract session name from subsession path.
    
    Args:
        subsession_path: Path to subsession directory
        
    Returns:
        Session name (parent directory name)
    """
    return subsession_path.parent.name


def get_subsession_name(subsession_path: Path) -> str:
    """
    Extract subsession name from path.
    
    Args:
        subsession_path: Path to subsession directory
        
    Returns:
        Subsession name (directory name)
    """
    return subsession_path.name
