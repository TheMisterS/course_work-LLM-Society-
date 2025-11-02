import logging
from logger import setup_logger
from utils.result_formatting import format_results, save_graph_image
from utils.config_formatting import save_configuration_snapshot
# TEMP/TEST imports
from graph.graph_factory import build_graph, initialize_state
from graph.utils.prompts import build_system_prompt, build_user_prompt
from IPython.display import Image, display

if __name__ == "__main__":
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting the LLM Society application")

    state = initialize_state()
    graph = build_graph()
    
    save_graph_image(graph, filename="graph.png")


    result = graph.invoke(state, {"recursion_limit": 100})


    format_results(result)
    save_configuration_snapshot()
    print(result)
    

    # TESTING

    # # Test state initialization
    # state = initialize_state()
    # print(state)

    # # Test prompt building
    # state = initialize_state()
    # for agent_name, agent_state in state["agents"].items():
    #     sys_prompt = build_system_prompt(agent_state)
    #     user_prompt = build_user_prompt(agent_state)
    #     print(f"System Prompt for {agent_name}:\n{sys_prompt}\n")
    #     print("----------------------------------------------------\n")
    #     print(f"User Prompt for {agent_name}:\n{user_prompt}\n")
    #     print("----------------------------------------------------\n")

