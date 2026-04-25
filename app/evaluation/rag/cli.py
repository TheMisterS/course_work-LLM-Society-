import argparse
from pathlib import Path


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evaluation/rag",
        description="RAG evaluation: persona distinctiveness and cross-run stability.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # per-subsession distinctiveness
  python evaluation/rag/main.py --subsession results/session_X/subsession_Y
  python evaluation/rag/main.py --session results/session_X
  python evaluation/rag/main.py --sessions results/ --output eval_outputs/rag/results.json

  # cross-run stability (--stability requires --session)
  python evaluation/rag/main.py --stability --session results/session_rag_only --output eval_outputs/rag/stability.json
        """,
    )

    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--subsession",
        type=Path,
        metavar="PATH",
        help="evaluate a single subsession",
    )
    target_group.add_argument(
        "--session",
        type=Path,
        metavar="PATH",
        help="evaluate all subsessions in a session (or stability session when --stability is set)",
    )
    target_group.add_argument(
        "--sessions",
        type=Path,
        nargs="+",
        metavar="PATH",
        help="evaluate all subsessions across multiple session directories",
    )

    parser.add_argument(
        "--stability",
        action="store_true",
        help="run cross-run stability mode instead of per-subsession distinctiveness (requires --session)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        metavar="PATH",
        help="output file path (default: auto-generated)",
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="output format for normal mode (default: json)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="suppress progress output",
    )

    return parser

def parse_args() -> argparse.Namespace:
    return create_parser().parse_args()
