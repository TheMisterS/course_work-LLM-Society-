import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from cli import parse_args
from loader import discover_sessions, discover_subsessions
from models import AggregatedResults, SubsessionResult
from output import print_summary, save_csv, save_json, save_subsession_result
import persona_distinctiveness
import rag_stability

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def evaluate_subsession_path(
    subsession_path: Path,
    results: AggregatedResults,
    verbose: bool = True,
) -> None:
    """Run distinctiveness on one subsession and add to results."""

    if verbose:
        logger.info("evaluating subsession: %s", subsession_path.name)

    try:
        metrics = persona_distinctiveness.compute(subsession_path)
    except FileNotFoundError as e:
        logger.warning("skipping %s: %s", subsession_path.name, e)
        return

    session_name = subsession_path.parent.name
    debate_topic = ""

    result = SubsessionResult(
        session_name=session_name,
        subsession_name=subsession_path.name,
        debate_topic=debate_topic,
        plane="rag",
        metrics=metrics,
    )

    results.add(result)
    save_subsession_result(result, subsession_path, "rag")


def evaluate_session_path(
    session_path: Path,
    results: AggregatedResults,
    verbose: bool = True,
) -> None:
    """Run distinctiveness on all subsessions in a session."""

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


def run_stability(session_path: Path, output_path: Path | None = None) -> None:
    """Run cross-run stability across all subsessions in a session."""

    if output_path is None:
        timestamp = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
        output_path = Path(f"stability_results_{timestamp}.json")

    rag_stability.compute(session_path, output_path)


def main() -> int:
    args = parse_args()
    verbose = not args.quiet

    if args.stability:
        if args.session is None:
            logger.error("--stability requires --session PATH")
            return 1
        if not args.session.exists():
            logger.error("session path does not exist: %s", args.session)
            return 1
        run_stability(args.session, args.output)
        return 0

    results = AggregatedResults(plane="rag")

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
        output_path = Path(f"rag_results_{timestamp}.{args.format}")

    if args.format == "csv":
        save_csv(results, output_path)
    else:
        save_json(results, output_path)

    if verbose:
        print_summary(results)

    return 0

if __name__ == "__main__":
    sys.exit(main())
