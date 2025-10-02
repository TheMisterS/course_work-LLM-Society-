
from graph.utils.state import GraphState
class Nodes:

    def __init__(self, state: GraphState):
        self.state = state


    def supervisor(state: GraphState):
        notes = state.get("supervisor_notes", [])

        speakers_length = len(state["agents"])

        #retrieve next speaker (might need to randomize each phase)
        speaker = list(state["agents"].keys())[state["round"] % speakers_length]
        
        notes += [f"Supervisor selects: {speaker} | phase={state['phase']} | round={state['round']}"]

        #(WIP) State shifting skeleton

        # if state["round"] == 5 and state["phase"] == "debate":
        #     phase = "role_shift"
        #     notes += ["Switching to role_shift."]
        # elif state["round"] == 7 and state["phase"] in ("debate","role_shift"):
        #     phase = "vote"
        #     notes += ["Switching to vote."]
        # else:
        #     phase = state["phase"]
        #return {"supervisor_notes": notes, "next_speaker": speaker, "phase": phase}

        return {"supervisor_notes": notes, "next_speaker": speaker}

    def agent_speak(state: GraphState, *, next_speaker: str):
        ...
    
    def remember(state: GraphState, *, next_speaker: str) -> Dict[str, Any]:
        ...


    #increments round and goes back to supervisor
    def tick(state: GraphState) -> Dict[str, Any]:
        #return {"round": state["round"] + 1}
        ...

    #Add conditional edge after this node
    # def route_after_supervisor(state: graph_state) -> str:
    #     if state["phase"] == "role_shift":
    #         return "role_shift"
    #     if state["phase"] == "vote":
    #         return "vote"
    #     return "agent_speak"

    #Route after agent interaction, either end or to tick to increment round
    def router(state: GraphState) -> str:
        ...

    #WIP for later
    def vote(state: GraphState) -> Dict[str, Any]:
        ...