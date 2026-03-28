from graph.utils.state import IndividualPersona
from data.types import Question, ResponseType

import logging
logger = logging.getLogger(__name__)


def generate_individual_system_prompt(persona: IndividualPersona) -> str:
    """Create a system prompt that describes the persona's demographics and instructs them to answer questions briefly and in character."""
    logger.debug("Generating individual system prompt")
    demo_lines = "\n".join(f"- {k}: {v}" for k, v in persona["demographics"].items())
    return (
        f"You are a person with the following background:\n{demo_lines}\n\n"
        "Answer each question briefly and in character."
    )


def generate_individual_user_prompt(question: Question) -> str:
    """Format the question with its response options so the LLM sees the full context."""
    logger.debug(f"Generating individual user prompt for question: {question.key!r}")
    parts = [f"Interviewer: {question.text}"]

    if question.response_type == ResponseType.LIKERT and question.options:
        opts = ", ".join(f"{k}={v}" for k, v in sorted(question.options.items()))
        parts.append(f"\nPlease choose one of the following options: {opts}")
    elif question.response_type == ResponseType.SCALE:
        lo = question.scale_labels.get(question.scale_min, str(question.scale_min))
        hi = question.scale_labels.get(question.scale_max, str(question.scale_max))
        parts.append(
            f"\nPlease answer on a scale from {question.scale_min} ({lo}) "
            f"to {question.scale_max} ({hi})."
        )
    elif question.response_type == ResponseType.CATEGORICAL and question.options:
        opts = ", ".join(f"{k}={v}" for k, v in sorted(question.options.items()))
        parts.append(f"\nOptions: {opts}")

    return "\n".join(parts)


def generate_individual_structured_user_prompt(question: Question) -> str:
    """Format the question and require strict JSON output for parser-friendly answers."""
    logger.debug(f"Generating individual structured user prompt for question: {question.key!r}")
    parts = [f"Interviewer: {question.text}"]

    if question.response_type in {ResponseType.LIKERT, ResponseType.CATEGORICAL} and question.options:
        opts = ", ".join(f"{k}={v}" for k, v in sorted(question.options.items()))
        parts.append(f"Valid codes: {opts}")
        parts.append(
            "Respond with ONLY valid JSON in this exact format: "
            '{"answer": <integer_code>}'
        )
    elif question.response_type == ResponseType.SCALE:
        lo = question.scale_min
        hi = question.scale_max
        lo_label = question.scale_labels.get(lo, str(lo))
        hi_label = question.scale_labels.get(hi, str(hi))
        parts.append(f"Scale bounds: {lo} ({lo_label}) to {hi} ({hi_label}).")
        parts.append(
            "Respond with ONLY valid JSON in this exact format: "
            '{"answer": <integer_in_range>}'
        )
    else:
        parts.append(
            "Respond with ONLY valid JSON in this exact format: "
            '{"answer": <number>}'
        )

    return "\n".join(parts)
