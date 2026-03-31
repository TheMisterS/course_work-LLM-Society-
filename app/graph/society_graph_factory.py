from langgraph.graph import StateGraph, END, START

from configs.agent_config import AGENT_PROFILES
from configs.models_config import MODEL_PROFILES, configure_model
from configs.simulation_config import (
    DEBATE_TOPIC, 
    VOTING_OPTIONS, 
    VOTING_QUESTION,
    LONG_MEMORY_ENABLED,
    LONG_MEMORY_UPDATE_INTERVAL
)
from graph.utils.state import AgentState, GraphState
from graph.utils.nodes import Nodes

import logging
logger = logging.getLogger(__name__)

# Conditional edges
def route_after_supervisor(state: GraphState) -> str:
    """
    Determine the next node after the supervisor based on the current phase.
    """

    if state["phase"] == "role_shift":
        return "role_shift"
    if state["phase"] == "vote":
        return "vote"
    return "agent_speak"

def route_after_update_memory(state: GraphState) -> str:
    """
    Determine the next node after update_memory based on the current phase
    and whether long memory update is needed.
    """
    logger.debug("***IN ROUTE AFTER UPDATE MEMORY***")
    
    if state["phase"] == "END":
        logger.debug("Routing to END: phase is END")
        return "END"
    
    # Check if long memory is enabled and if it's time to update
    if LONG_MEMORY_ENABLED:
        current_round = state["round"]
        if current_round % LONG_MEMORY_UPDATE_INTERVAL == 0:
            logger.debug(f"Routing to update_long_memory: round {current_round} is at interval {LONG_MEMORY_UPDATE_INTERVAL}")
            return "update_long_memory"
        else:
            logger.debug(f"Routing to supervisor: round {current_round} not at long memory interval")
    else:
        logger.debug("Routing to supervisor: long memory disabled")
    
    return "supervisor"

# main functions
def initialize_state(personas=None):
    """
    Initialize the graph state with agents, models, and default values.

    Args:
        personas: Optional List[GeneratedPersona] from the RAG pipeline. Each
                  stakeholder becomes one agent. Falls back to static AGENT_PROFILES when None or empty.
    """
    state = GraphState()
    state["agents"] = {}
    state["models"] = {}

    # Build agent list - RAG personas take priority, AGENT_PROFILES forfallback
    if personas:
        for persona in personas:
            agent_state = AgentState(
                name=persona["name"],
                role_desc=persona["role_desc"],
                keypoints=persona["keypoints"],
                long_mem=[],
                short_mem=[],
                agent_agenda={"debate_topic": DEBATE_TOPIC}
            )
            state["agents"][persona["name"]] = agent_state
    else:
        for agent_name, profile in AGENT_PROFILES.items():
            agent_state = AgentState(
                name=agent_name,
                role_desc=profile["role_desc"],
                keypoints=profile["keypoints"],
                long_mem=[],
                short_mem=[],
                agent_agenda={"debate_topic": DEBATE_TOPIC}
            )
            state["agents"][agent_name] = agent_state

    # Initialize models
    for model_number, profile in MODEL_PROFILES.items():
        state["models"][model_number] = configure_model(profile)

    # Initialize other attributes
    state["round"] = 0
    state["phase"] = "debate"
    state["supervisor_notes"] = []
    state["agenda"] = {"debate_topic": DEBATE_TOPIC}
    state["messages"] = []
    state["votes"] = {}
    state["voting_question"] = VOTING_QUESTION
    state["voting_options"] = VOTING_OPTIONS

    return state

def build_graph():
    """
    Build and return the state graph for the simulation.
    """
    
    logger.debug("Building the state graph.")
    logger.debug(f"Long memory feature enabled: {LONG_MEMORY_ENABLED}")
    
    workflow = StateGraph(GraphState)
    nodes = SocietyNodes()
    
    #Nodes
    workflow.add_node("supervisor", nodes.supervisor)
    workflow.add_node("agent_speak", nodes.agent_speak)
    workflow.add_node("update_memory", nodes.update_short_memory)
    workflow.add_node("vote", nodes.vote)
    
    # conditionally add long memory node
    if LONG_MEMORY_ENABLED:
        workflow.add_node("update_long_memory", nodes.update_long_memory)


    #Edges
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
    "supervisor", route_after_supervisor, {
       "agent_speak": "agent_speak",
       "vote": "vote"
      }
    )
    workflow.add_edge("agent_speak", "update_memory")
    
    # conditional routing after update_memory based on long memory config
    if LONG_MEMORY_ENABLED:
        logger.debug("Configuring edges with long memory routing")
        workflow.add_conditional_edges("update_memory", route_after_update_memory, {
            "END": END,
            "supervisor": "supervisor",
            "update_long_memory": "update_long_memory"
        })
        workflow.add_edge("update_long_memory", "supervisor")
    else:
        logger.debug("Configuring edges without long memory routing")
        workflow.add_conditional_edges("update_memory", route_after_update_memory, {
            "END": END,
            "supervisor": "supervisor"
        })
    workflow.add_edge("vote", END)

    ...
    graph = workflow.compile()

    return graph



