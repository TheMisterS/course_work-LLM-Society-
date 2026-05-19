import json
from pathlib import Path

def load_personas(subsession_path: Path) -> list[dict]:
    """Load personas list from rag/07_personas.json."""
    
    personas_file = subsession_path / "rag" / "07_personas.json"
    
    if not personas_file.exists():
        raise FileNotFoundError(
            f"rag/07_personas.json not found in {subsession_path}. "
            "Ensure the RAG pipeline ran for this subsession."
        )
        
    with open(personas_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return data["personas"]


def load_state(subsession_path: Path) -> dict:
    state_files = list(subsession_path.glob("state_*.json"))
    
    if not state_files:
        raise FileNotFoundError(f"No state_*.json found in {subsession_path}.")
    
    with open(state_files[0], "r", encoding="utf-8") as f:
        return json.load(f)


def discover_subsessions(session_path: Path) -> list[Path]:
    
    subsessions = []
    
    for item in session_path.iterdir():
        if item.is_dir() and item.name.startswith("subsession_"):
            subsessions.append(item)
            
    return sorted(subsessions)


def discover_sessions(results_path: Path) -> list[Path]:
    
    sessions = []
    
    for item in results_path.iterdir():
        if item.is_dir() and item.name.startswith("session_"):
            sessions.append(item)
            
    return sorted(sessions)
