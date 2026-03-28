from __future__ import annotations

from datetime import datetime
from pathlib import Path

from evaluation.cli import build_parser
from evaluation.scorer import (
    compute_metrics,
    write_json_report,
    write_question_csv,
)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    summary, question_metrics, diagnostics = compute_metrics(
        batch_path=args.batch,
        ground_truth_path=args.ground_truth,
        strict_source_id=args.strict_source_id,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_dir = Path(__file__).resolve().parent.parent.parent / "results"
    out_json = args.out_json or (default_dir / f"evaluation_{timestamp}.json")
    out_csv = args.out_csv or (default_dir / f"evaluation_{timestamp}_questions.csv")

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
