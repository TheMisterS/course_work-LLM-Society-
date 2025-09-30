from typing import TypedDict, List, Dict, Literal, Optional
from langgraph.graph import add_messages

class Msg(TypedDict):
    role: Literal["system","user","assistant","agent","supervisor"]
    name: Optional[str]
    content: str
class AgentProfile(TypedDict):
    role_desc: str
    traits: Dict[str, str] 

class AgentState(TypedDict):
    name: str
    role_desc: str
    traits: Dict[str, str]
    long_mem: List[str]
    short_mem: List[Msg]

class SocietyState(TypedDict):
    messages: List[Msg]
    agents: Dict[str, AgentState]
    profiles: Dict[str, AgentProfile]
    round: int
    phase: Literal["debate","vote","interview","done"]
    supervisor_notes: List[str]
    agenda: Dict[str, str]
    votes: Dict[str, str]

reducers = {
    "messages": add_messages,
    "supervisor_notes": list.__add__,
}