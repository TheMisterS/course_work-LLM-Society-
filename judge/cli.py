"""
CLI for the Judge system.
"""

import argparse
from pathlib import Path

from config import settings


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="judge",
        description="LLM-as-Judge evaluation system for multi-agent debates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate a single subsession
  python main.py --subsession ./results/session_2025.12.23/subsession_2025.12.23_00.22.49

  # Evaluate all subsessions in a session
  python main.py --session ./results/session_2025.12.23

  # Evaluate multiple sessions
  python main.py --sessions ./results/session_2025.12.22 ./results/session_2025.12.23

  # Specify model and output format
  python main.py --subsession ./path/to/subsession --model llama3.2 --format json

  # Custom output path
  python main.py --session ./results/session_2025.12.23 --output ./my_results.csv
        """
    )
    
    # Evaluation target
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--subsession",
        type=Path,
        metavar="PATH",
        help="Path to a single subsession directory to evaluate"
    )
    target_group.add_argument(
        "--session",
        type=Path,
        metavar="PATH",
        help="Path to a session directory (evaluates all subsessions)"
    )
    target_group.add_argument(
        "--sessions",
        type=Path,
        nargs="+",
        metavar="PATH",
        help="Paths to multiple session directories to evaluate"
    )
    
    # Model configuration
    parser.add_argument(
        "--model",
        type=str,
        default=settings.ollama_model,
        help=f"Ollama model to use for evaluation (default: {settings.ollama_model})"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=settings.ollama_temperature,
        help=f"Model temperature (default: {settings.ollama_temperature})"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=settings.ollama_base_url,
        help=f"Ollama API base URL (default: {settings.ollama_base_url})"
    )
    parser.add_argument(
        "--num-ctx",
        type=int,
        default=settings.ollama_num_ctx,
        help=f"Context window size (default: {settings.ollama_num_ctx})"
    )
    
    # Output configuration
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        metavar="PATH",
        help="Output file path (default: auto-generated in current directory)"
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["csv", "json"],
        default=settings.default_output_format,
        help=f"Output format (default: {settings.default_output_format})"
    )
    
    # Other options
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress messages"
    )
    
    return parser


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = create_parser()
    return parser.parse_args()
