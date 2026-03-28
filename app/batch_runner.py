"""
Batch interview runner.

Iterates over all validated personas, runs the individual interview graph
for each one, and exports a CSV of either raw free-form responses or
structured numeric answers (depending on configured mode) for comparison
with ground-truth answers in ``answers.csv``.
"""

from __future__ import annotations

import csv
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List

from configs.models_config import MODEL_PROFILES
from configs.individual_config import INDIVIDUAL_ANSWER_MODE, MODEL_USED_FOR_INDIVIDUAL
from data.datasets.ess_11_lt import load_questions, load_personas
from data.types import Persona, Question
from graph.chain_factory import create_agent_chain
from graph.utils.answer_parser import parse_structured_answer
from graph.individual_graph_factory import (
    build_individual_graph,
    initialize_individual_state,
)
from graph.utils.individual_prompts import (
    generate_individual_structured_user_prompt,
    generate_individual_system_prompt,
    generate_individual_user_prompt,
)

logger = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def _run_persona_with_batched_requests(
    state: dict,
    questions: List[Question],
    structured_mode: bool,
) -> dict[str, dict[str, str | int | float]]:
    """Run all question prompts for one persona in a single batched chain call."""
    model = state["models"][MODEL_USED_FOR_INDIVIDUAL]
    chain = create_agent_chain(model)

    system_prompt = generate_individual_system_prompt(state["persona"])
    batch_inputs = []
    for question in questions:
        if structured_mode:
            user_prompt = generate_individual_structured_user_prompt(question)
        else:
            user_prompt = generate_individual_user_prompt(question)
        batch_inputs.append(
            {
                "system_message": system_prompt,
                "user_message": user_prompt,
            }
        )

    raw_responses = chain.batch(batch_inputs)

    answers: dict[str, str] = {}
    answers_structured: dict[str, int | float | str] = {}
    for question, response in zip(questions, raw_responses):
        answers[question.key] = response
        if structured_mode:
            try:
                answers_structured[question.key] = parse_structured_answer(response, question)
            except ValueError as exc:
                logger.warning(
                    "Failed to parse structured answer for question %r in batched mode: %s",
                    question.key,
                    exc,
                )
                answers_structured[question.key] = ""

    return {
        "answers": answers,
        "answers_structured": answers_structured,
    }


def run_batch(
    personas: List[Persona] | None = None,
    questions: List[Question] | None = None,
) -> Path:
    """Interview every persona and export results to a timestamped CSV.

    Returns the path to the generated CSV file.
    """
    personas = personas or load_personas(validated=True)
    questions = questions or load_questions(validated=True)

    profile = MODEL_PROFILES.get(MODEL_USED_FOR_INDIVIDUAL)
    if profile is None:
        raise ValueError(
            f"MODEL_USED_FOR_INDIVIDUAL={MODEL_USED_FOR_INDIVIDUAL!r} not found in MODEL_PROFILES"
        )
    provider = profile.get("provider", "ollama")
    use_batched_requests = provider in {"openai", "openrouter"}

    graph = build_individual_graph() if not use_batched_requests else None
    question_keys = [q.key for q in questions]
    structured_mode = INDIVIDUAL_ANSWER_MODE == "structured"
    logger.info(f"[batch] Individual answer mode: {INDIVIDUAL_ANSWER_MODE}")
    logger.info(
        "[batch] Individual provider=%s, batched_requests=%s",
        provider,
        use_batched_requests,
    )

    # ---- create CSV up front and persist each persona row immediately ----
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS_DIR / f"batch_{timestamp}.csv"
    fieldnames = ["source_id"] + question_keys

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        f.flush()
        os.fsync(f.fileno())

        for i, persona in enumerate(personas):
            sid = persona.source_id or str(i)
            logger.info(f"[batch] Interviewing persona {i + 1}/{len(personas)}  (source_id={sid})")
            print(f"\n{'=' * 60}")
            print(f"  Persona {i + 1}/{len(personas)}  —  source_id={sid}")
            print(f"{'=' * 60}")

            state = initialize_individual_state(persona=persona, questions=questions)
            if use_batched_requests:
                result = _run_persona_with_batched_requests(
                    state=state,
                    questions=questions,
                    structured_mode=structured_mode,
                )
            else:
                result = graph.invoke(state, {"recursion_limit": len(questions) * 2 + 10})

            row: dict[str, str | int | float] = {"source_id": sid}
            if structured_mode:
                llm_answers = result.get("answers_structured", {})
            else:
                llm_answers = result.get("answers", {})
            for key in question_keys:
                row[key] = llm_answers.get(key, "")

            writer.writerow(row)
            # Force durability for long batch runs in case process stops unexpectedly.
            f.flush()
            os.fsync(f.fileno())

    logger.info(f"[batch] Results written to {csv_path}")
    print(f"\n✓ Batch complete — {len(personas)} personas × {len(question_keys)} questions")
    print(f"  Results saved to: {csv_path}")
    return csv_path
