import argparse
import logging
from logger import setup_logger
from utils.result_formatting import create_subsession_folder, format_results, save_graph_image, export_state_to_json
from utils.config_formatting import save_configuration_snapshot
from rag import build_persona_context
from baseline.pipeline import build_persona_context_no_rag

from configs.simulation_config import DEBATE_TOPIC
# TEMP DISCUSSION IMPORTS
from graph.graph_factory import build_graph, initialize_state

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Society simulation")
    parser.add_argument("--mode", choices=["rag", "baseline"], default="rag",
                        help="Persona generation mode: 'rag' (web-grounded) or 'baseline' (general knowledge only)")
    args = parser.parse_args()

    setup_logger()
    logger = logging.getLogger(__name__)

    logger.info("=" * 40)
    logger.info("Simulation mode: %s", args.mode.upper())
    logger.info("=" * 40)

    logger.info("Starting the LLM Society application")

    subsession_path = create_subsession_folder()

    if args.mode == "rag":
        personas = build_persona_context(DEBATE_TOPIC, output_dir=subsession_path)
    else:
        personas = build_persona_context_no_rag(DEBATE_TOPIC, output_dir=subsession_path)

    for p in personas:
        logger.info("[personas] %s | keypoints: %s", p["name"], p["keypoints"])

    state = initialize_state(personas=personas)
    graph = build_graph()

    save_graph_image(graph, filename="graph.png")

    result = graph.invoke(state, {"recursion_limit": 100})

    format_results(result, subsession_path=subsession_path)
    export_state_to_json(result, subsession_path)
    save_configuration_snapshot(subsession_path, personas=personas, mode=args.mode)
