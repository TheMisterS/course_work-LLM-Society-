import argparse
from pathlib import Path


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="evaluation/votes",
        description="Vote evaluation: entropy, stance alignment, and vote changes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        
Examples:
  python evaluation/votes/main.py --subsession results/session_X/subsession_Y
  python evaluation/votes/main.py --session results/session_X
  python evaluation/votes/main.py --sessions results/ --output eval_outputs/votes/results.json
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
        help="evaluate all subsessions in a session",
    )
    target_group.add_argument(
        "--sessions",
        type=Path,
        nargs="+",
        metavar="PATH",
        help="evaluate all subsessions across multiple session directories",
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
        help="output format (default: json)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="suppress progress output",
    )

    return parser


def parse_args() -> argparse.Namespace:
    return create_parser().parse_args()
