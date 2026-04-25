"""
Standalone RAG-only runner.
Runs the RAG pipeline and saves rag/ artifacts without starting the debate.
Usage:
    python rag_runner.py
    python rag_runner.py --session results/session_2026.04.06
"""

import argparse
import os
import sys
import logging
from pathlib import Path

# load .env from the app/ directory regardless of where this script is invoked from
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from configs.simulation_config import DEBATE_TOPIC
from rag.pipeline import build_persona_context
from utils.result_formatting import create_subsession_folder
from utils.time_and_dates import date_stamp, date_time_stamp


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def create_subsession_under(session_path: str) -> str:
    """Create a new subsession_* folder inside an existing session folder."""
    
    subsession_name = f"subsession_{date_time_stamp()}"
    subsession_path = os.path.join(session_path, subsession_name)
    
    os.makedirs(session_path, exist_ok=True)
    os.makedirs(subsession_path, exist_ok=True)
    
    return subsession_path


def log_personas(personas) -> None:
    logger.info("generated %d persona(s):", len(personas))
    for p in personas:
        logger.info("  name: %s | affiliation: %s | stance: %s | keypoints: %d",
                    p['name'], p['affiliation'], p['stance'], len(p['keypoints']))


def parse_args():
    
    parser = argparse.ArgumentParser(description="Run RAG pipeline only, without starting the debate.")
    
    parser.add_argument(
        "--session",
        type=str,
        default=None,
        metavar="PATH",
        help="Existing session folder to create a new subsession under (e.g. results/session_2026.04.06)"
    )
    
    return parser.parse_args()


def main() -> int:
    
    args = parse_args()

    if args.session:
        subsession_path = create_subsession_under(args.session)
    else:
        # auto-create session_YYYY.MM.DD/subsession_* under results/
        subsession_path = create_subsession_folder()

    logger.info("subsession folder: %s", subsession_path)
    logger.info("topic: %s", DEBATE_TOPIC)

    personas = build_persona_context(DEBATE_TOPIC, output_dir=subsession_path)

    log_personas(personas)
    logger.info("rag artifacts saved to: %s/rag/", subsession_path)
    logger.info("personas file: %s", os.path.join(subsession_path, "rag", "07_personas.json"))

    return 0

if __name__ == "__main__":
    sys.exit(main())
