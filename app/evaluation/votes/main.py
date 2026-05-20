import argparse
import json
import logging
import sys
from pathlib import Path

# got into some ModuleNotFoundError issues when running from ./app :) 
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from loader import discover_subsessions
import stance_vote_alignment
import vote_change_through_rounds
import vote_distribution

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _session_extremes(all_subsession_metrics: list[dict]) -> dict:
    """Find min/max values for each numeric metric across all subsessions & maintain key  on which session/subsession."""
    extremes: dict = {}

    for entry in all_subsession_metrics:
        session = entry["session"]
        subsession = entry["subsession"]
        for key, val in entry["metrics"].items():
            if not isinstance(val, (int, float)):
                continue

            if key not in extremes:
                extremes[key] = {
                    "min": {"value": val, "session": session, "subsession": subsession},
                    "max": {"value": val, "session": session, "subsession": subsession},
                }
                continue

            if val < extremes[key]["min"]["value"]:
                extremes[key]["min"] = {"value": val, "session": session, "subsession": subsession}
            if val > extremes[key]["max"]["value"]:
                extremes[key]["max"] = {"value": val, "session": session, "subsession": subsession}
    return extremes


def main():
    
    parser = argparse.ArgumentParser(prog="evaluation/votes")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--session",
        type=Path,
        metavar="PATH",
        help="evaluate all subsessions in a session",
    )
    group.add_argument(
        "--subsession",
        type=Path,
        metavar="PATH",
        help="evaluate a single subsession",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        metavar="PATH",
        help="output file path (default: auto-generated in the session/subsession dir)",
    )
    args = parser.parse_args()

    # --subsession: evaluate a single subsession
    if args.subsession:
        subsession_path = args.subsession
        if not subsession_path.exists():
            logger.error("path does not exist: %s", subsession_path)
            return 1
        
        try:
            metrics = {}
            metrics.update(stance_vote_alignment.compute(subsession_path))
            metrics.update(vote_change_through_rounds.compute(subsession_path))
            metrics.update(vote_distribution.compute(subsession_path))
        except FileNotFoundError as e:
            logger.error("could not load state: %s", e)
            return 1

        output_path = args.output or subsession_path / "eval" / "votes_metrics.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
            
        logger.info("saved to: %s", output_path)
        return 0
    
    # --session: evaluate all subsessions
    else:
        session_path = args.session
        if not session_path.exists():
            logger.error("session path does not exist: %s", session_path)
            return 1

        subsessions = discover_subsessions(session_path)
        if not subsessions:
            logger.error("no subsessions found in %s", session_path)
            return 1

        logger.info("found %d subsession(s) in %s", len(subsessions), session_path.name)

        all_subsession_metrics = []
        for subsession in subsessions:
            logger.info("evaluating subsession: %s", subsession.name)
            try:
                metrics = {}
                metrics.update(stance_vote_alignment.compute(subsession))
                metrics.update(vote_change_through_rounds.compute(subsession))
                metrics.update(vote_distribution.compute(subsession))
            except FileNotFoundError as exception:
                logger.warning("skipping %s: %s", subsession.name, exception)
                continue

            all_subsession_metrics.append({
                "session": session_path.name,
                "subsession": subsession.name,
                "metrics": metrics,
            })

            sub_output = subsession / "eval" / "votes_metrics.json"
            sub_output.parent.mkdir(parents=True, exist_ok=True)
            
            with open(sub_output, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)

        if not all_subsession_metrics:
            logger.error("no results collected — check that state_*.json exists")
            return 1

        # strip metadata for easier/cleaner aggregation
        only_metrics = [entry["metrics"] for entry in all_subsession_metrics]

        session_aggregate = {}
        session_aggregate.update(stance_vote_alignment.aggregate(only_metrics))
        session_aggregate.update(vote_change_through_rounds.aggregate(only_metrics))
        session_aggregate.update(vote_distribution.aggregate(only_metrics))

        output = {
            "session": session_path.name,
            "num_subsessions": len(all_subsession_metrics),
            "aggregate": session_aggregate,
            "session_extremes": _session_extremes(all_subsession_metrics),
            "subsessions": all_subsession_metrics,
        }

        output_path = args.output or session_path / "eval" / "votes_metrics.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        logger.info("saved results to: %s", output_path)

        return 0

if __name__ == "__main__":
    sys.exit(main())
