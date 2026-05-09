import argparse
import json
import logging
import os
from logger import setup_logger
from utils.result_formatting import create_results_folder, format_results, save_graph_image, export_state_to_json
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
    parser.add_argument("--personas-only", action="store_true",
                        help="Generate personas and save them, then exit without running the discussion")
    parser.add_argument("--persona-file", type=str, default=None, metavar="PATH",
                        help="Path to a 07_personas.json from a previous run. Skips persona generation.")
    args = parser.parse_args()

    setup_logger()
    logger = logging.getLogger(__name__)

    logger.info("=" * 40)
    logger.info("Simulation mode: %s", args.mode.upper())
    logger.info("=" * 40)

    logger.info("Starting the LLM Society application")

    subsession_path = create_results_folder(args.mode)

    if args.persona_file:
        with open(args.persona_file, "r", encoding="utf-8") as f:
            personas = json.load(f)["personas"]
        logger.info("Loaded %d personas from file: %s", len(personas), args.persona_file)
        
        # also save the personas from the target dir to subsession so the metrics pick it up correctly
        rag_dir = os.path.join(subsession_path, "rag")
        os.makedirs(rag_dir, exist_ok=True)
        with open(os.path.join(rag_dir, "07_personas.json"), "w", encoding="utf-8") as f:
            json.dump({"total": len(personas), "personas": personas}, f, ensure_ascii=False, indent=2)\
                
    elif args.mode == "rag":
        personas = build_persona_context(DEBATE_TOPIC, output_dir=subsession_path)
    else:
        personas = build_persona_context_no_rag(DEBATE_TOPIC, output_dir=subsession_path)

    for p in personas:
        logger.info("[personas] %s | keypoints: %s", p["name"], p["keypoints"])

    if args.personas_only:
        save_configuration_snapshot(subsession_path, personas=personas, mode=args.mode,
                                    persona_source=args.persona_file)
        logger.info("--personas-only: skipping discussion. Results saved to %s", subsession_path)
    else:
        state = initialize_state(personas=personas)
        graph = build_graph()

        save_graph_image(graph, filename="graph.png")

        result = graph.invoke(state, {"recursion_limit": 100})

        format_results(result, subsession_path=subsession_path)
        export_state_to_json(result, subsession_path)
        save_configuration_snapshot(subsession_path, personas=personas, mode=args.mode,
                                    persona_source=args.persona_file)
