
class Nodes:

    def supervisor(state: SocietyState):
        ...

    def agent_speak(state: SocietyState, *, next_speaker: str):
        ...
    
    def remember(state: SocietyState, *, next_speaker: str) -> Dict[str, Any]:
        ...


    #increments round and goes back to supervisor
    def tick(state: SocietyState) -> Dict[str, Any]:
        #return {"round": state["round"] + 1}
        ...

    #Add conditional edge after this node
    def route_after_supervisor(state: SocietyState) -> str:
        ...

    #Route after agent interaction, either end or to tick to increment round
    def router(state: SocietyState) -> str:
        ...

    #WIP for later
    def vote(state: SocietyState) -> Dict[str, Any]:
        ...