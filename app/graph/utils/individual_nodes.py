from graph.utils.state import IndividualState, Msg
from graph.utils.individual_prompts import (
    generate_individual_system_prompt,
    generate_individual_user_prompt,
    generate_individual_structured_user_prompt,
)
from graph.utils.answer_parser import parse_structured_answer
from graph.chain_factory import create_agent_chain
from configs.individual_config import MODEL_USED_FOR_INDIVIDUAL, INDIVIDUAL_ANSWER_MODE

import logging
logger = logging.getLogger(__name__)


class IndividualInterviewNodes:

    def persona_respond(self, state: IndividualState) -> dict:
        """Emit the interviewer question, generate the persona's answer, then advance the index."""
        logger.debug("***IN PERSONA_RESPOND NODE***")
        persona = state["persona"]
        idx = state["current_question_index"]
        question = state["questions"][idx]  # Question dataclass
        logger.debug(f"Processing question {idx + 1}: {question.key!r}")

        system_prompt = generate_individual_system_prompt(persona)
        if INDIVIDUAL_ANSWER_MODE == "structured":
            user_prompt = generate_individual_structured_user_prompt(question)
        else:
            user_prompt = generate_individual_user_prompt(question)

        model = state["models"][MODEL_USED_FOR_INDIVIDUAL]
        chain = create_agent_chain(model)

        response = chain.invoke({
            "system_message": system_prompt,
            "user_message": user_prompt,
        })

        logger.debug(f"Persona responded to question {idx + 1}")
        print(f"\n[Interviewer]: {question.text}")
        if INDIVIDUAL_ANSWER_MODE == "structured":
            try:
                parsed_value = parse_structured_answer(response, question)
                print(f"[Respondent raw]: {response}")
                print(f"[Respondent parsed]: {parsed_value}\n")
            except ValueError as exc:
                parsed_value = ""
                logger.warning(
                    "Failed to parse structured answer for question %r: %s",
                    question.key,
                    exc,
                )
                print(f"[Respondent raw]: {response}")
                print("[Respondent parsed]: <invalid>\n")
        else:
            parsed_value = ""
            print(f"[Respondent]: {response}\n")
        print("-" * 60)

        question_message = Msg(role="user", name="Interviewer", content=question.text)
        answer_message = Msg(role="agent", name="Respondent", content=response)

        # Accumulate answers keyed by question key
        answers = dict(state.get("answers", {}))
        answers[question.key] = response
        answers_structured = dict(state.get("answers_structured", {}))
        if INDIVIDUAL_ANSWER_MODE == "structured":
            answers_structured[question.key] = parsed_value

        next_index = idx + 1
        phase = "done" if next_index >= len(state["questions"]) else "individual"

        result = {
            "messages": [question_message, answer_message],
            "current_question_index": next_index,
            "phase": phase,
            "answers": answers,
        }
        if INDIVIDUAL_ANSWER_MODE == "structured":
            result["answers_structured"] = answers_structured
        return result
