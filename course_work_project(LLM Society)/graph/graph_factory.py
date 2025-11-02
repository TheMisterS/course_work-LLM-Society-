from langgraph.graph import StateGraph, END, START

from configs.agent_config import AGENT_PROFILES
from configs.models_config import MODEL_PROFILES
from configs.simulation_config import DEBATE_TOPIC, VOTING_OPTIONS, VOTING_QUESTION
from graph.utils.state import AgentState, GraphState
from graph.chain_factory import configure_model
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

def route_after_tick(state: GraphState) -> str:
    """
    Determine the next node after the tick based on the current phase.
    """
    if state["phase"] == "END":
        return "END"
    return "supervisor"

# main functions
def initialize_state():
    """
    Initialize the graph state with agents, models, and default values.
    """
    state = GraphState()
    state["agents"] = {}
    state["models"] = {}

    # Initialize agents
    for agent_name, profile in AGENT_PROFILES.items():
        agent_state = AgentState(
            name=agent_name,
            role_desc=profile["role_desc"],
            traits=profile["traits"],
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
    workflow = StateGraph(GraphState)
    nodes = Nodes()
    
    #Nodes
    workflow.add_node("supervisor", nodes.supervisor)
    workflow.add_node("agent_speak", nodes.agent_speak)
    workflow.add_node("update_memory", nodes.update_memory)
    workflow.add_node("tick", nodes.tick)
    workflow.add_node("vote", nodes.vote)


    #Edges
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
    "supervisor", route_after_supervisor, {
       "agent_speak": "agent_speak",
       "vote": "vote"
      }
    )
    workflow.add_edge("agent_speak", "update_memory")
    workflow.add_edge("update_memory", "tick")
    workflow.add_conditional_edges("tick", route_after_tick, {
        "END": END,
        "supervisor": "supervisor"
    })

    ...
    graph = workflow.compile()

    return graph



