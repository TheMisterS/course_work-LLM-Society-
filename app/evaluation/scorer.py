from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from data.datasets.ess_11_lt import _ANSWERS_PATH


@dataclass
class EvaluationSummary:
    batch_path: str
    ground_truth_path: str
    batch_rows: int
    truth_rows: int
    matched_rows: int
    batch_only_rows: int
    truth_only_rows: int
    compared_question_count: int
    compared_cell_count: int
    valid_batch_cell_count: int
    overall_cell_exact_match_rate: float
    row_all_questions_exact_match_rate: float


@dataclass
class QuestionMetrics:
    question: str
    compared_cells: int
    valid_batch_cells: int
    missing_count: int
    invalid_count: int
    exact_matches: int
    exact_match_rate: float


def load_answers_csv(path: Path) -> pd.DataFrame:
    """Load answers CSV with source_id as string and all values as string."""
    df = pd.read_csv(path, encoding="utf-8", dtype=str)
    if "source_id" not in df.columns:
        raise ValueError(f"CSV missing required column 'source_id': {path}")
    return df


def _to_numeric_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def compute_metrics(
    batch_path: Path,
    ground_truth_path: Path | None = None,
    strict_source_id: bool = False,
) -> tuple[EvaluationSummary, list[QuestionMetrics], list[str]]:
    """Compare LLM batch output with ground-truth answers and return metrics."""
    gt_path = ground_truth_path or _ANSWERS_PATH

    batch_df = load_answers_csv(batch_path)
    truth_df = load_answers_csv(gt_path)

    batch_ids = set(batch_df["source_id"].dropna().astype(str))
    truth_ids = set(truth_df["source_id"].dropna().astype(str))

    shared_ids = batch_ids & truth_ids
    batch_only = batch_ids - truth_ids
    truth_only = truth_ids - batch_ids

    diagnostics: list[str] = []
    if batch_only:
        diagnostics.append(f"Batch has {len(batch_only)} source_id values not in ground truth")
    if truth_only:
        diagnostics.append(f"Ground truth has {len(truth_only)} source_id values not in batch")

    if strict_source_id and (batch_only or truth_only):
        raise ValueError(
            "source_id mismatch under strict mode: "
            f"batch_only={len(batch_only)}, truth_only={len(truth_only)}"
        )

    batch_df = batch_df[batch_df["source_id"].astype(str).isin(shared_ids)].copy()
    truth_df = truth_df[truth_df["source_id"].astype(str).isin(shared_ids)].copy()

    batch_df = batch_df.sort_values("source_id")
    truth_df = truth_df.sort_values("source_id")

    question_cols = sorted(
        (set(batch_df.columns) & set(truth_df.columns)) - {"source_id"}
    )

    if not shared_ids:
        diagnostics.append("No shared source_id values found between batch and ground truth")
    if not question_cols:
        diagnostics.append("No shared question columns found between batch and ground truth")

    per_question: list[QuestionMetrics] = []
    total_compared_cells = 0
    total_valid_batch_cells = 0
    total_exact_matches = 0

    if shared_ids and question_cols:
        merged = batch_df[["source_id"] + question_cols].merge(
            truth_df[["source_id"] + question_cols],
            on="source_id",
            suffixes=("_batch", "_truth"),
        )

        row_all_exact_count = 0
        for _, row in merged.iterrows():
            row_exact = True
            for q in question_cols:
                b_raw = row[f"{q}_batch"]
                t_raw = row[f"{q}_truth"]

                b_num = pd.to_numeric(pd.Series([b_raw]), errors="coerce").iloc[0]
                t_num = pd.to_numeric(pd.Series([t_raw]), errors="coerce").iloc[0]

                if pd.isna(b_num) or pd.isna(t_num) or b_num != t_num:
                    row_exact = False
                    break
            if row_exact:
                row_all_exact_count += 1

        for q in question_cols:
            batch_num = _to_numeric_series(merged[f"{q}_batch"])
            truth_num = _to_numeric_series(merged[f"{q}_truth"])

            valid_mask = batch_num.notna() & truth_num.notna()
            compared_cells = int(valid_mask.sum())
            exact_matches = int((batch_num[valid_mask] == truth_num[valid_mask]).sum())

            missing_count = int(merged[f"{q}_batch"].isna().sum() + (merged[f"{q}_batch"].astype(str) == "").sum())
            invalid_count = int(batch_num.isna().sum() - missing_count)
            valid_batch_cells = int(batch_num.notna().sum())

            exact_rate = (exact_matches / compared_cells) if compared_cells else 0.0

            per_question.append(
                QuestionMetrics(
                    question=q,
                    compared_cells=compared_cells,
                    valid_batch_cells=valid_batch_cells,
                    missing_count=missing_count,
                    invalid_count=max(invalid_count, 0),
                    exact_matches=exact_matches,
                    exact_match_rate=exact_rate,
                )
            )

            total_compared_cells += compared_cells
            total_valid_batch_cells += valid_batch_cells
            total_exact_matches += exact_matches

        row_all_questions_exact_match_rate = (
            row_all_exact_count / len(merged) if len(merged) else 0.0
        )
    else:
        row_all_questions_exact_match_rate = 0.0

    overall_cell_exact_match_rate = (
        total_exact_matches / total_compared_cells if total_compared_cells else 0.0
    )

    summary = EvaluationSummary(
        batch_path=str(batch_path),
        ground_truth_path=str(gt_path),
        batch_rows=len(batch_ids),
        truth_rows=len(truth_ids),
        matched_rows=len(shared_ids),
        batch_only_rows=len(batch_only),
        truth_only_rows=len(truth_only),
        compared_question_count=len(question_cols),
        compared_cell_count=total_compared_cells,
        valid_batch_cell_count=total_valid_batch_cells,
        overall_cell_exact_match_rate=overall_cell_exact_match_rate,
        row_all_questions_exact_match_rate=row_all_questions_exact_match_rate,
    )
    return summary, per_question, diagnostics


def write_json_report(
    out_path: Path,
    summary: EvaluationSummary,
    question_metrics: list[QuestionMetrics],
    diagnostics: list[str],
) -> None:
    payload: dict[str, Any] = {
        "summary": asdict(summary),
        "per_question": [asdict(m) for m in question_metrics],
        "diagnostics": diagnostics,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_question_csv(out_path: Path, question_metrics: list[QuestionMetrics]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "question",
                "compared_cells",
                "valid_batch_cells",
                "missing_count",
                "invalid_count",
                "exact_matches",
                "exact_match_rate",
            ],
        )
        writer.writeheader()
        for metric in question_metrics:
            writer.writerow(asdict(metric))
