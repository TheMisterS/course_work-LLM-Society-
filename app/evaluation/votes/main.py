import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from cli import parse_args
from loader import discover_sessions, discover_subsessions
from models import AggregatedResults, SubsessionResult
from output import print_summary, save_csv, save_json, save_subsession_result
import vote_entropy
import stance_vote_alignment
import vote_change

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _compute_all_metrics(subsession_path: Path) -> dict:
    metrics = {}
    metrics.update(vote_entropy.compute(subsession_path))
    metrics.update(stance_vote_alignment.compute(subsession_path))
    metrics.update(vote_change.compute(subsession_path))
    return metrics


def evaluate_subsession_path(
    subsession_path: Path,
    results: AggregatedResults,
    verbose: bool = True,
) -> None:
    
    if verbose:
        logger.info("evaluating subsession: %s", subsession_path.name)

    try:
        metrics = _compute_all_metrics(subsession_path)
    except FileNotFoundError as e:
        logger.warning("skipping %s: %s", subsession_path.name, e)
        return

    session_name = subsession_path.parent.name

    result = SubsessionResult(
        session_name=session_name,
        subsession_name=subsession_path.name,
        debate_topic="",
        plane="votes",
        metrics=metrics,
    )

    results.add(result)
    save_subsession_result(result, subsession_path, "votes")


def evaluate_session_path(
    session_path: Path,
    results: AggregatedResults,
    verbose: bool = True,
) -> None:
    if verbose:
        logger.info("processing session: %s", session_path.name)

    subsessions = discover_subsessions(session_path)

    if not subsessions:
        logger.warning("no subsessions found in %s", session_path)
        return

    if verbose:
        logger.info("found %d subsession(s)", len(subsessions))

    for subsession_path in subsessions:
        evaluate_subsession_path(subsession_path, results, verbose)


def _cache_session_extremes(results: AggregatedResults) -> dict:
    """track which subsession had the min/max for each numeric metric."""
    extremes: dict = {}

    for r in results.subsessions:
        for key, val in r.metrics.items():
            if not isinstance(val, (int, float)):
                continue

            if key not in extremes:
                extremes[key] = {
                    "min": {"value": val, "session": r.session_name, "subsession": r.subsession_name},
                    "max": {"value": val, "session": r.session_name, "subsession": r.subsession_name},
                }
                continue

            if val < extremes[key]["min"]["value"]:
                extremes[key]["min"] = {"value": val, "session": r.session_name, "subsession": r.subsession_name}
            if val > extremes[key]["max"]["value"]:
                extremes[key]["max"] = {"value": val, "session": r.session_name, "subsession": r.subsession_name}

    return extremes


def _save_with_extremes(results: AggregatedResults, output_path: Path) -> None:
    """save the normal aggregated json + attach session extremes."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = results.to_dict()
    data["session_extremes"] = _cache_session_extremes(results)
    data["timestamp"] = datetime.now().isoformat()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("saved JSON with session extremes to: %s", output_path)


def main() -> int:
    args = parse_args()
    verbose = not args.quiet

    results = AggregatedResults(plane="votes")
    
    # check if we have multiple subsessions, if yes -> save extremes
    is_session_run = args.session is not None or args.sessions is not None

    if args.subsession:
        if not args.subsession.exists():
            logger.error("subsession path does not exist: %s", args.subsession)
            return 1
        evaluate_subsession_path(args.subsession, results, verbose)

    elif args.session:
        if not args.session.exists():
            logger.error("session path does not exist: %s", args.session)
            return 1
        evaluate_session_path(args.session, results, verbose)

    elif args.sessions:
        for session_path in args.sessions:
            if not session_path.exists():
                logger.warning("session path does not exist: %s", session_path)
                continue
            evaluate_session_path(session_path, results, verbose)

    if not results.subsessions:
        logger.error("no results collected — check input paths")
        return 1

    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
        output_path = Path(f"votes_results_{timestamp}.{args.format}")

    if args.format == "csv":
        save_csv(results, output_path)
    elif is_session_run:
        # json + extremes only when we have multiple subsessions to compare
        _save_with_extremes(results, output_path)
    else:
        save_json(results, output_path)

    if verbose:
        print_summary(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
