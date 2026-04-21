import argparse
import logging
from logger import setup_logger
from utils.result_formatting import create_subsession_folder, format_results, save_graph_image, export_state_to_json
from utils.config_formatting import save_configuration_snapshot
from rag import build_persona_context

from configs.simulation_config import DEBATE_TOPIC
# TEMP DISCUSSION IMPORTS
from graph.graph_factory import build_graph, initialize_state
from graph.utils.prompts import generate_debate_system_prompt, generate_debate_user_prompt
from IPython.display import Image, display

if __name__ == "__main__":
    setup_logger()
    logger = logging.getLogger(__name__)
    
#   Main application entry point
    logger.info("Starting the LLM Society application")

    subsession_path = create_subsession_folder()

    personas = build_persona_context(DEBATE_TOPIC, output_dir=subsession_path)

    for p in personas:
        logger.info("[personas] %s | keypoints: %s", p["name"], p["keypoints"])

    state = initialize_state(personas=personas)
    graph = build_graph()
    
    save_graph_image(graph, filename="graph.png")

    result = graph.invoke(state, {"recursion_limit": 100})

    format_results(result, subsession_path=subsession_path)
    export_state_to_json(result, subsession_path)
    save_configuration_snapshot(subsession_path, personas=personas)

    # TESTING

    # # Test state initialization
    # state = initialize_state()
    # print(state)

    # # Test debate prompt building
    # state = initialize_state()
    # for agent_name, agent_state in state["agents"].items():
    #     sys_prompt = generate_debate_system_prompt(agent_state)
    #     user_prompt = generate_debate_user_prompt(agent_state)
    #     print(f"System Prompt for {agent_name}:\n{sys_prompt}\n")
    #     print("----------------------------------------------------\n")
    #     print(f"User Prompt for {agent_name}:\n{user_prompt}\n")
    #     print("----------------------------------------------------\n")

