import argparse
import logging
from logger import setup_logger
from utils.result_formatting import format_results, save_graph_image, export_state_to_json
from utils.config_formatting import save_configuration_snapshot
# TEMP/TEST imports
from graph.society_graph_factory import build_graph, initialize_state
from graph.utils.prompts import generate_debate_system_prompt, generate_debate_user_prompt
from IPython.display import Image, display

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Society simulation")
    parser.add_argument(
        "--mode",
        choices=["society", "individual"],
        default="society",
        help="Run mode: 'society' (group debate) or 'individual' (single persona interview)",
    )
    args = parser.parse_args()

    setup_logger()
    logger = logging.getLogger(__name__)

    if args.mode == "individual":
        logger.info("Starting in INDIVIDUAL mode")
        from graph.individual_graph_factory import build_individual_graph, initialize_individual_state

        state = initialize_individual_state()
        graph = build_individual_graph()
        result = graph.invoke(state, {"recursion_limit": 200})

    else:
        logger.info("Starting in SOCIETY mode")
        from graph.society_graph_factory import build_graph, initialize_state

        state = initialize_state()
        graph = build_graph()
        result = graph.invoke(state, {"recursion_limit": 100})

        # subsession_path = format_results(result)
        # export_state_to_json(result, subsession_path)
        # save_configuration_snapshot(subsession_path)

    print(result)
    

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

