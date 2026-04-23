import sys
from pathlib import Path

from aggregator import generate_output_filename, print_summary, save_metrics
from cli import parse_args
from evaluator import JudgeEvaluator
from models import AggregatedMetrics
from parser import discover_sessions, discover_subsessions


def evaluate_subsession_path(
    evaluator: JudgeEvaluator,
    subsession_path: Path,
    metrics: AggregatedMetrics,
    verbose: bool = True
) -> None:
    """
    Evaluate a single subsession and add to metrics.
    
    Args:
        evaluator: JudgeEvaluator instance
        subsession_path: Path to subsession directory
        metrics: AggregatedMetrics to add results to
        verbose: Print progress messages
    """
    result = evaluator.evaluate_subsession(subsession_path, verbose=verbose)
    if result:
        metrics.add_subsession(result)


def evaluate_session_path(
    evaluator: JudgeEvaluator,
    session_path: Path,
    metrics: AggregatedMetrics,
    verbose: bool = True
) -> None:
    """
    Evaluate all subsessions in a session.
    
    Args:
        evaluator: JudgeEvaluator instance
        session_path: Path to session directory
        metrics: AggregatedMetrics to add results to
        verbose: Print progress messages
    """
    if verbose:
        print(f"\nProcessing session: {session_path.name}")
    
    subsessions = discover_subsessions(session_path)
    if not subsessions:
        print(f"  No subsessions found in {session_path}")
        return
    
    if verbose:
        print(f"  Found {len(subsessions)} subsession(s)")
    
    for subsession_path in subsessions:
        evaluate_subsession_path(evaluator, subsession_path, metrics, verbose)


def main() -> int:
    args = parse_args()
    verbose = not args.quiet
    
    if verbose:
        print("=" * 60)
        print("LLM-as-Judge Evaluation System")
        print("=" * 60)
        print(f"Model: {args.model}")
        print(f"Temperature: {args.temperature}")
        print(f"Output format: {args.format}")
        print("=" * 60)
    
    # Initialize evaluator
    evaluator = JudgeEvaluator(
        model=args.model,
        temperature=args.temperature,
        base_url=args.base_url,
        num_ctx=args.num_ctx,
    )
    
    # Initialize metrics container
    metrics = AggregatedMetrics()
    
    # Process based on mode
    if args.subsession:
        # Single subsession mode
        if not args.subsession.exists():
            print(f"Error: Subsession path does not exist: {args.subsession}")
            return 1
        evaluate_subsession_path(evaluator, args.subsession, metrics, verbose)
    
    elif args.session:
        # Single session mode
        if not args.session.exists():
            print(f"Error: Session path does not exist: {args.session}")
            return 1
        evaluate_session_path(evaluator, args.session, metrics, verbose)
    
    elif args.sessions:
        # Multiple sessions mode
        for session_path in args.sessions:
            if not session_path.exists():
                print(f"Warning: Session path does not exist: {session_path}")
                continue
            evaluate_session_path(evaluator, session_path, metrics, verbose)
    
    # Check if we have results
    if not metrics.subsessions:
        print("No results to save. Check your input paths.")
        return 1
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = Path(generate_output_filename(args.format))
    
    # Save results
    save_metrics(metrics, output_path, args.format)
    
    if verbose:
        print_summary(metrics)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
