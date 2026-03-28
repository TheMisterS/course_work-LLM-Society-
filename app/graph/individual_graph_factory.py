from langgraph.graph import StateGraph, END, START

from configs.individual_config import (
    INDIVIDUAL_PROFILE,
    INDIVIDUAL_QUESTION_OBJECTS,
    INDIVIDUAL_PERSONA,
)
from configs.models_config import MODEL_PROFILES
from graph.utils.state import IndividualPersona, IndividualState
from graph.chain_factory import configure_model
from graph.utils.individual_nodes import IndividualInterviewNodes
from data.types import Persona, Question
from typing import List, Optional

import logging
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Conditional edge
# ---------------------------------------------------------------------------

def route_after_response(state: IndividualState) -> str:
    if state["phase"] == "done":
        logger.debug("All questions answered — routing to END")
        return "END"
    logger.debug(f"Routing back to persona_respond (next index: {state['current_question_index']})")
    return "persona_respond"


# ---------------------------------------------------------------------------
# State initialisation
# ---------------------------------------------------------------------------

def initialize_individual_state(
    persona: Optional[Persona] = None,
    questions: Optional[List[Question]] = None,
) -> IndividualState:
    """Build the initial state for an individual interview.

    Parameters
    ----------
    persona : Persona, optional
        Override the default persona loaded from config.
    questions : list[Question], optional
        Override the default question list loaded from config.
    """
    p = persona or INDIVIDUAL_PERSONA
    q = questions or INDIVIDUAL_QUESTION_OBJECTS

    ind_persona: IndividualPersona = {
        "demographics": {k: str(v) for k, v in p.attributes.items()},
    }

    models = {}
    for model_key, profile in MODEL_PROFILES.items():
        models[model_key] = configure_model(profile)

    state: IndividualState = {
        "persona": ind_persona,
        "questions": q,
        "current_question_index": 0,
        "messages": [],
        "phase": "individual",
        "models": models,
        "answers": {},
        "answers_structured": {},
        "source_id": p.source_id,
    }

    logger.debug(
        f"Individual state initialised — {len(ind_persona['demographics'])} demographic fields, "
        f"{len(q)} questions, source_id={p.source_id}"
    )
    return state


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_individual_graph():
    logger.debug("Building individual interview graph")

    workflow = StateGraph(IndividualState)
    nodes = IndividualInterviewNodes()

    workflow.add_node("persona_respond", nodes.persona_respond)

    workflow.add_edge(START, "persona_respond")
    workflow.add_conditional_edges(
        "persona_respond",
        route_after_response,
        {
            "persona_respond": "persona_respond",
            "END": END,
        },
    )

    graph = workflow.compile()
    logger.debug("Individual interview graph compiled successfully")
    return graph
