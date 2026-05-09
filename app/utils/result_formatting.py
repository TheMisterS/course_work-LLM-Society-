
import os
import logging
import json

logger = logging.getLogger(__name__)

from utils.time_and_dates import date_stamp, date_time_stamp

def create_results_folder(mode: str, base_result_directory: str = "results") -> str:
    """
    Create the session_*/subsession_* folder structure and return the subsession path.
        mode: Simulation mode ('rag' or 'baseline'), appended to the session folder name.
        base_result_directory: Root results directory (default: "results").
    """
    os.makedirs(base_result_directory, exist_ok=True)

    folder_mode = "no_rag" if mode == "baseline" else mode
    session_folder_path = os.path.join(base_result_directory, f"session_{date_stamp()}_{folder_mode}")
    os.makedirs(session_folder_path, exist_ok=True)

    subsession_folder_path = os.path.join(session_folder_path, f"subsession_{date_time_stamp()}")
    os.makedirs(subsession_folder_path, exist_ok=True)

    return subsession_folder_path


def format_results(results: dict, base_result_directory: str = "results", subsession_path: str = None):
    """
    Store conversation logs, supervisor notes, votes, and long-term memory summaries.
        results: The final graph state dict.
        base_result_directory: Root results directory, used only when subsession_path is None.
        subsession_path: Pre-created subsession folder path. If provided, folder creation is
            skipped and files are written directly into this path.

    """

    if subsession_path is not None:
        subsession_folder_path = subsession_path
    else:
        subsession_folder_path = create_results_folder(base_result_directory)

    current_time_stamp = date_time_stamp()

    # Define file paths/names for logs
    conversation_file = os.path.join(subsession_folder_path, f"conversations_{current_time_stamp}.txt")
    supervisor_notes_file = os.path.join(subsession_folder_path, f"supervisor_notes_{current_time_stamp}.txt")
    votes_file = os.path.join(subsession_folder_path, f"votes_{current_time_stamp}.txt")
    long_term_memory_file = os.path.join(subsession_folder_path, f"long_term_memory_{current_time_stamp}.txt")


    # Conversation Log
    with open(conversation_file, "w", encoding="utf-8") as f:
        for message in results["messages"]:
            if message:
                f.write(f"[{message['name']}]: {message['content']}\n")
                f.write("-" * 80 + "\n")  

    # Supervisor Notes Log
    with open(supervisor_notes_file, "w", encoding="utf-8") as f:
        for note in results["supervisor_notes"]:
            if note: 
                f.write(f"{note}\n")
                f.write("=" * 80 + "\n\n")

    # Votes Log
    with open(votes_file, "w", encoding="utf-8") as f:
        for round_label, round_votes in results.get("votes", {}).items():
            f.write(f"=== {round_label.upper()} VOTE ===\n")
            for agent_name, v in round_votes.items():
                f.write(f"[{agent_name}]\n")
                f.write(f"VOTE: {v.get('vote', '')}\n")
                f.write(f"REASON: {v.get('reason', '')}\n")
                f.write("-" * 80 + "\n")
            f.write("\n")

    # Long-Term Memory Log
    with open(long_term_memory_file, "w", encoding="utf-8") as f:
        for agent_name, agent_state in results.get("agents", {}).items():
            f.write("=" * 80 + "\n")
            f.write(f"=== AGENT: {agent_name} ===\n")
            f.write("=" * 80 + "\n\n")
            
            long_mem = agent_state.get("long_mem", [])
            if long_mem:
                for idx, summary in enumerate(long_mem, 1):
                    f.write(f"[Summary #{idx}]\n")
                    f.write(f"{summary}\n")
                    f.write("-" * 80 + "\n\n")
            else:
                f.write("No long-term memory summaries recorded.\n\n")
    
    return subsession_folder_path


def export_state_to_json(results: dict, subsession_folder_path: str):
    """
    Export the final state to a JSON file.
        results: The final state dict
        subsession_folder_path: Path to the subsession folder

    """
    current_time_stamp = date_time_stamp()
    json_file = os.path.join(subsession_folder_path, f"state_{current_time_stamp}.json")
    
    serializable_state = {
        "messages": results.get("messages", []),
        "agents": {},
        "round": results.get("round", 0),
        "phase": results.get("phase", "done"),
        "supervisor_notes": results.get("supervisor_notes", []),
        "agenda": results.get("agenda", {}),
        "next_speaker": results.get("next_speaker", None),
        "votes": results.get("votes", {}),
        "voting_options": results.get("voting_options", []),
        "voting_question": results.get("voting_question", "")
    }
    
    for agent_name, agent_state in results.get("agents", {}).items():
        serializable_state["agents"][agent_name] = {
            "name": agent_state.get("name", agent_name),
            "role_desc": agent_state.get("role_desc", ""),
            "keypoints": agent_state.get("keypoints", []),
            "long_mem": agent_state.get("long_mem", []),
            "short_mem": agent_state.get("short_mem", []),
            "agent_agenda": agent_state.get("agent_agenda", {})
        }
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(serializable_state, f, indent=2, ensure_ascii=False)
    
    logger.info(f"State exported to JSON: {json_file}")
    return json_file
    

def save_graph_image(graph, filename="graph.png"):
    """
    Draw the graph and save it to a PNG file.
    
    Args:
        graph: The graph object to visualize
        filename: The output filename (default: "graph.png")
    """
    png_data = graph.get_graph().draw_mermaid_png()
    with open(filename, "wb") as f:
        f.write(png_data)
    logger = logging.getLogger(__name__)
    logger.info(f"Graph visualization saved to {filename}")

