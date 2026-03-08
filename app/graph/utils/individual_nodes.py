from graph.utils.state import IndividualState, Msg
from graph.utils.individual_prompts import (
    generate_individual_system_prompt,
    generate_individual_user_prompt,
)
from graph.chain_factory import create_agent_chain
from configs.individual_config import MODEL_USED_FOR_INDIVIDUAL

import logging
logger = logging.getLogger(__name__)


class IndividualInterviewNodes:

    def persona_respond(self, state: IndividualState) -> dict:
        """Emit the interviewer question, generate the persona's answer, then advance the index."""
        logger.debug("***IN PERSONA_RESPOND NODE***")
        persona = state["persona"]
        idx = state["current_question_index"]
        question = state["questions"][idx]
        logger.debug(f"Processing question {idx + 1}: {question!r}")

        system_prompt = generate_individual_system_prompt(persona)
        user_prompt = generate_individual_user_prompt(question)

        model = state["models"][MODEL_USED_FOR_INDIVIDUAL]
        chain = create_agent_chain(model)

        response = chain.invoke({
            "system_message": system_prompt,
            "user_message": user_prompt,
        })

        logger.debug(f"Persona responded to question {idx + 1}")
        print(f"\n[Interviewer]: {question}")
        print(f"[Respondent]: {response}\n")
        print("-" * 60)

        question_message = Msg(role="user", name="Interviewer", content=question)
        answer_message = Msg(role="agent", name="Respondent", content=response)

        next_index = idx + 1
        phase = "done" if next_index >= len(state["questions"]) else "individual"

        return {
            "messages": [question_message, answer_message],
            "current_question_index": next_index,
            "phase": phase,
        }
