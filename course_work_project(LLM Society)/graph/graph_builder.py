

def build_graph():
    ...



#Examples!
# graph.add_node("supervisor", supervisor)
# graph.add_node("agent_speak", agent_speak)
# graph.add_node("remember", remember)
# graph.add_node("role_shift", role_shift)
# graph.add_node("vote", vote)
# graph.add_node("tick", tick)

# graph.add_edge("supervisor", route_after_supervisor)
# graph.add_edge("role_shift", "tick")
# graph.add_edge("vote", "tick")
# graph.add_edge("agent_speak", "remember")
# graph.add_edge("remember", router)
# graph.add_edge("tick", "supervisor")