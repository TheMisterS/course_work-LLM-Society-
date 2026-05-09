import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from loader import discover_subsessions
import persona_similarity_in_subsession as in_subsession
import persona_similarity_across_sessions as across_sessions

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(prog="evaluation/rag")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--session",
        type=Path,
        metavar="PATH",
        help="evaluate all subsessions in a session and compute both metrics",
    )
    group.add_argument(
        "--subsession",
        type=Path,
        metavar="PATH",
        help="evaluate a single subsession (in-subsession metrics only)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        metavar="PATH",
        help="output file path (default: auto-generated in the session/subsession dir)",
    )
    args = parser.parse_args()

    if args.subsession:
        subsession_path = args.subsession
        if not subsession_path.exists():
            logger.error("path does not exist: %s", subsession_path)
            return 1

        try:
            metrics = in_subsession.compute(subsession_path)
        except FileNotFoundError as e:
            logger.error("could not load personas: %s", e)
            return 1

        # set output path
        output_path = args.output
        if output_path is None:
            output_path = subsession_path / "eval" / "rag_metrics.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
            
        logger.info("saved to: %s", output_path)
        
        return 0
    
    # --session: compute both metrics in one pass
    else:
        session_path = args.session
        if not session_path.exists():
            logger.error("session path does not exist: %s", session_path)
            return 1

        subsession_paths = discover_subsessions(session_path)
        if not subsession_paths:
            logger.error("no subsessions found in %s", session_path)
            return 1

        logger.info("found %d subsession(s) in %s", len(subsession_paths), session_path.name)

        subsession_metrics = []
        for sub_path in subsession_paths:
            logger.info("computing in-subsession metrics: %s", sub_path.name)
            
            try:
                metrics = in_subsession.compute(sub_path)
            except FileNotFoundError as e:
                logger.warning("skipping %s: %s", sub_path.name, e)
                continue

            subsession_metrics.append(metrics)

            sub_output = sub_path / "eval" / "persona_metrics.json"
            sub_output.parent.mkdir(parents=True, exist_ok=True)
            
            with open(sub_output, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)

        if not subsession_metrics:
            logger.error("no subsession metrics collected — check that rag/07_personas.json exists")
            return 1

        in_subsession_aggregate = in_subsession.aggregate(subsession_metrics)

        output = {
            "session": session_path.name,
            "num_subsessions": len(subsession_metrics),
            "in_subsession_aggregate": in_subsession_aggregate,
        }

        if len(subsession_paths) >= 2:
            logger.info("computing similarity across all sessions")
            output["across_sessions"] = across_sessions.compute(session_path)
        else:
            logger.info("skipping all session similarity (need >= 2 subsessions, found %d)", len(subsession_paths))

        # set output path
        output_path = args.output
        if output_path is None:
            output_path = session_path / "eval" / "persona_metrics.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        logger.info("saved combined results to: %s", output_path)

        return 0


if __name__ == "__main__":
    sys.exit(main())
