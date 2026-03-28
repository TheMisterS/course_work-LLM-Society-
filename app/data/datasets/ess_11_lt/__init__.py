"""
ESS Round 11 – Lithuania dataset loaders.

Usage:
    questions: list[Question] = load_questions()
    personas:  list[Persona]  = load_personas()
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pandas as pd

from data.types import Persona, Question, ResponseType

_DIR = Path(__file__).resolve().parent
_VALIDATED_DIR = _DIR / "human_validated_dataset"
_ANSWERS_PATH  = _DIR / "answers.csv"


def load_questions(validated: bool = False) -> List[Question]:
    """Load questions from ``questions.json`` into ``Question`` dataclass instances.

    Parameters
    ----------
    validated : bool
        When *True*, load from the ``human_validated_dataset/`` subdirectory.
    """
    questions_path = (_VALIDATED_DIR if validated else _DIR) / "questions.json"
    raw: list[dict] = json.loads(questions_path.read_text(encoding="utf-8"))
    questions: list[Question] = []
    for entry in raw:
        options = {int(k): v for k, v in entry.get("options", {}).items()}
        scale_labels = {int(k): v for k, v in entry.get("scale_labels", {}).items()}
        questions.append(
            Question(
                key=entry["key"],
                text=entry["text"],
                response_type=ResponseType(entry["response_type"]),
                options=options,
                scale_min=entry.get("scale_min"),
                scale_max=entry.get("scale_max"),
                scale_labels=scale_labels,
            )
        )
    return questions

def load_personas(validated: bool = False) -> List[Persona]:
    """Load respondent profiles from ``personas.csv`` into ``Persona`` dataclass instances.

    Parameters
    ----------
    validated : bool
        When *True*, load personas from the ``human_validated_dataset/`` subdirectory.

    If ``answers.csv`` exists alongside ``personas.csv``, each persona's
    ``answers`` dict is populated with the raw coded survey responses
    (question key → int/float).  Otherwise ``answers`` stays empty.
    """
    personas_path = (_VALIDATED_DIR if validated else _DIR) / "personas.csv"
    df = pd.read_csv(personas_path, encoding="utf-8", dtype=str)

    # load answers keyed by source_id (if file exists)
    answers_by_id: dict[str, dict[str, int | float | str]] = {}
    if _ANSWERS_PATH.exists():
        adf = pd.read_csv(_ANSWERS_PATH, encoding="utf-8", dtype={"source_id": str})
        for _, arow in adf.iterrows():
            sid = str(arow.get("source_id", ""))
            ans: dict[str, int | float | str] = {}
            for k, v in arow.drop(labels="source_id").items():
                if pd.isna(v):
                    continue
                try:
                    ans[k] = int(v)
                except (ValueError, TypeError):
                    try:
                        ans[k] = float(v)
                    except (ValueError, TypeError):
                        ans[k] = str(v)
            answers_by_id[sid] = ans

    personas: list[Persona] = []
    for _, row in df.iterrows():
        source_id = row.get("source_id")
        attrs: dict[str, int | float | str] = {}
        for k, v in row.drop(labels="source_id").items():
            if pd.isna(v) or v == "":
                continue
            try:
                attrs[k] = int(v)
            except ValueError:
                try:
                    attrs[k] = float(v)
                except ValueError:
                    attrs[k] = v
        personas.append(Persona(
            attributes=attrs,
            answers=answers_by_id.get(str(source_id), {}),
            source_id=source_id,
        ))
    return personas
