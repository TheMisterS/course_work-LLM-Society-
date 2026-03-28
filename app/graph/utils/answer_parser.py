from __future__ import annotations

import json
import re
from typing import Any

from data.types import Question, ResponseType


def _coerce_number(value: Any) -> float | int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            if re.fullmatch(r"[-+]?\d+", text):
                return int(text)
            return float(text)
        except ValueError:
            return None
    return None


def _extract_answer_field(raw_response: str) -> Any:
    text = raw_response.strip()
    if not text:
        raise ValueError("Empty model response")

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        # Fallback for models that wrap JSON in additional text.
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Response is not valid JSON")
        payload = json.loads(match.group(0))

    if not isinstance(payload, dict) or "answer" not in payload:
        raise ValueError("JSON payload must contain an 'answer' field")
    return payload["answer"]


def parse_structured_answer(raw_response: str, question: Question) -> int | float:
    """Parse and validate structured answer against question response type.

    Expected input from model is JSON like: {"answer": 3}
    Returns a normalized numeric value suitable for direct CSV comparison.
    """
    answer_value = _extract_answer_field(raw_response)
    parsed = _coerce_number(answer_value)
    if parsed is None:
        raise ValueError("Answer must be numeric")

    if question.response_type in {ResponseType.LIKERT, ResponseType.CATEGORICAL}:
        if int(parsed) != parsed:
            raise ValueError("Answer must be an integer code")
        code = int(parsed)
        if question.options and code not in question.options:
            raise ValueError(f"Answer code {code} is not in allowed options")
        return code

    if question.response_type == ResponseType.SCALE:
        if int(parsed) != parsed:
            raise ValueError("Scale answer must be an integer")
        value = int(parsed)
        if question.scale_min is not None and value < question.scale_min:
            raise ValueError(
                f"Scale answer {value} below minimum {question.scale_min}"
            )
        if question.scale_max is not None and value > question.scale_max:
            raise ValueError(
                f"Scale answer {value} above maximum {question.scale_max}"
            )
        return value

    # NUMERIC: keep int when possible, otherwise float.
    if int(parsed) == parsed:
        return int(parsed)
    return float(parsed)
