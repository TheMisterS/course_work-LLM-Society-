import argparse
import logging
from logger import setup_logger
from utils.result_formatting import format_results, save_graph_image, export_state_to_json
from utils.config_formatting import save_configuration_snapshot
# TEMP/TEST imports
from graph.society_graph_factory import build_graph, initialize_state
from graph.utils.prompts import generate_debate_system_prompt, generate_debate_user_prompt
from IPython.display import Image, display

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Society simulation")
    parser.add_argument(
        "--mode",
        choices=["society", "individual", "batch", "evaluate"],
        default="society",
        help=(
            "Run mode: 'society' (group debate), 'individual' (single persona interview), "
            "'batch' (all personas), or 'evaluate' (compare batch CSV vs ground truth)"
        ),
    )
    parser.add_argument(
        "--batch-path",
        default=None,
        help="Path to batch_*.csv for evaluation mode",
    )
    parser.add_argument(
        "--ground-truth-path",
        default=None,
        help="Optional path to ground-truth answers CSV for evaluation mode",
    )
    parser.add_argument(
        "--out-json",
        default=None,
        help="Optional output JSON path for evaluation report",
    )
    parser.add_argument(
        "--out-csv",
        default=None,
        help="Optional output CSV path for per-question evaluation report",
    )
    parser.add_argument(
        "--strict-source-id",
        action="store_true",
        help="Evaluation mode: fail if source_id sets do not match exactly",
    )
    args = parser.parse_args()

    setup_logger()
    logger = logging.getLogger(__name__)

    result = None

    if args.mode == "batch":
        logger.info("Starting in BATCH mode")
        from batch_runner import run_batch

        csv_path = run_batch()
        print(f"Batch results: {csv_path}")

    elif args.mode == "evaluate":
        logger.info("Starting in EVALUATE mode")
        if not args.batch_path:
            raise ValueError("--batch-path is required in evaluate mode")

        from pathlib import Path
        from evaluation.scorer import compute_metrics, write_json_report, write_question_csv
        from datetime import datetime

        summary, question_metrics, diagnostics = compute_metrics(
            batch_path=Path(args.batch_path),
            ground_truth_path=Path(args.ground_truth_path) if args.ground_truth_path else None,
            strict_source_id=args.strict_source_id,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_dir = Path(__file__).resolve().parent.parent / "results"
        out_json = Path(args.out_json) if args.out_json else default_dir / f"evaluation_{timestamp}.json"
        out_csv = (
            Path(args.out_csv)
            if args.out_csv
            else default_dir / f"evaluation_{timestamp}_questions.csv"
        )

        write_json_report(out_json, summary, question_metrics, diagnostics)
        write_question_csv(out_csv, question_metrics)

        print("Evaluation complete")
        print(f"  batch file: {summary.batch_path}")
        print(f"  ground truth: {summary.ground_truth_path}")
        print(f"  matched source_id rows: {summary.matched_rows}")
        print(f"  compared questions: {summary.compared_question_count}")
        print(f"  overall cell exact match: {summary.overall_cell_exact_match_rate:.4f}")
        print(
            "  row-level exact match (all questions): "
            f"{summary.row_all_questions_exact_match_rate:.4f}"
        )
        if diagnostics:
            print("  diagnostics:")
            for d in diagnostics:
                print(f"    - {d}")
        print(f"  json report: {out_json}")
        print(f"  question report: {out_csv}")

    elif args.mode == "individual":
        logger.info("Starting in INDIVIDUAL mode")
        from graph.individual_graph_factory import build_individual_graph, initialize_individual_state

        state = initialize_individual_state()
        graph = build_individual_graph()
        result = graph.invoke(state, {"recursion_limit": 200})

    else:
        logger.info("Starting in SOCIETY mode")
        from graph.society_graph_factory import build_graph, initialize_state

        state = initialize_state()
        graph = build_graph()
        result = graph.invoke(state, {"recursion_limit": 100})

        # subsession_path = format_results(result)
        # export_state_to_json(result, subsession_path)
        # save_configuration_snapshot(subsession_path)

    if result is not None:
        print(result)
    

    # TESTING

    # # Test state initialization
    # state = initialize_state()
    # print(state)

    # # Test debate prompt building
    # state = initialize_state()
    # for agent_name, agent_state in state["agents"].items():
    #     sys_prompt = generate_debate_system_prompt(agent_state)
    #     user_prompt = generate_debate_user_prompt(agent_state)
    #     print(f"System Prompt for {agent_name}:\n{sys_prompt}\n")
    #     print("----------------------------------------------------\n")
    #     print(f"User Prompt for {agent_name}:\n{user_prompt}\n")
    #     print("----------------------------------------------------\n")

