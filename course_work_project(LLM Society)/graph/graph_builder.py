from langgraph.graph import StateGraph, END
from types import SocietyState, reducers


def build_graph():
    workflow = StateGraph(SocietyState, reducers=reducers)

    
    # workflow.add_node("supervisor", supervisor)
    # workflow.add_node("agent_speak", agent_speak)
    # workflow.add_node("remember", remember)
    # workflow.add_node("role_shift", role_shift)
    # workflow.add_node("vote", vote)
    # workflow.add_node("tick", tick)

    # workflow.add_edge(START, "supervisor")
    # workflow.add_conditional_edge("supervisor",
    #   route_after_supervisor,
    #    "role_shift": "role_shift",
    #    "vote": "vote"
    #    "agent_speak": "agent_speak"
    #)
    # workflow.add_edge("role_shift", "tick")
    # workflow.add_edge("vote", "tick")
    # workflow.add_edge("agent_speak", "remember")
    # workflow.add_edge("remember", router)
    # workflow.add_edge("tick", "supervisor")
    ...
    graph = workflow.compile()

    return graph



