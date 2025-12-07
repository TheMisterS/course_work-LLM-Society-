
import os
import logging

logger = logging.getLogger(__name__)

from utils.time_and_dates import date_stamp, date_time_stamp

def format_results(results, base_result_directory="results"):
    """
    Creates a sessions & subsessions folder structure to store conversation logs, supervisor notes, votes, and long-term memory summaries.

    Args:
        base_directory: The base directory where the folder will be created

    Returns:
        subsession_folder_path: The path to the created subsession folder
    """

    if not os.path.exists(base_result_directory):
        logger.warning(f"Base result directory {base_result_directory} does not exist. Creating it.")
        os.makedirs(base_result_directory)

    current_date_stamp = date_stamp()
    current_time_stamp = date_time_stamp()

    # Create session folder
    session_folder_name = f"session_{current_date_stamp}"
    session_folder_path = os.path.join(base_result_directory, session_folder_name)
    os.makedirs(session_folder_path, exist_ok=True)

    # Create subsession folder
    subsession_folder_name = f"subsession_{current_time_stamp}"
    subsession_folder_path = os.path.join(session_folder_path, subsession_folder_name)
    os.makedirs(subsession_folder_path, exist_ok=True)

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
        for agent_name, vote in results.get("votes", {}).items():
            f.write(f"[{agent_name}]: {vote}\n")
            f.write("-" * 80 + "\n")

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

