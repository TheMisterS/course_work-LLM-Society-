
from datetime import datetime
import os
import logging
logger = logging.getLogger(__name__)

def format_results(results, base_result_directory="results"):
    """
    Creates a folder timestamped for the current day with two empty txt files.

    Args:
        base_directory: The base directory where the folder will be created

    Returns:
        tuple: (folder_path, conversation_file_path, supervisor_notes_file_path)
    """

    if not os.path.exists(base_result_directory):
        logger.warning(f"Base result directory {base_result_directory} does not exist. Creating it.")
        os.makedirs(base_result_directory)

    date_stamp = datetime.now().strftime("%Y.%m.%d")
    date_time_stamp = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")

    # Create folder name with date stamp
    folder_name = f"session_{date_stamp}"
    folder_path = os.path.join(base_result_directory, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    conversation_file = os.path.join(folder_path, f"conversations_{date_time_stamp}.txt")
    supervisor_notes_file = os.path.join(folder_path, f"supervisor_notes_{date_time_stamp}.txt")

    # Create files
    with open(conversation_file, "w", encoding="utf-8") as f:
        for message in results["messages"]:
            if message:
                f.write(f"[{message['name']}]: {message['content']}\n")
                f.write("-" * 80 + "\n")  


    with open(supervisor_notes_file, "w", encoding="utf-8") as f:
        for note in results["supervisor_notes"]:
            if note: 
                f.write(f"{note}\n")
                f.write("=" * 80 + "\n\n")

    return

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

