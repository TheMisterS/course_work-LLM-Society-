from graph.utils.state import IndividualPersona

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


def generate_individual_user_prompt(question: str) -> str:
    """make the question the user-prompt."""
    logger.debug(f"Generating individual user prompt for question: {question!r}")
    return f"Interviewer: {question}"
