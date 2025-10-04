from typing import TypedDict, List, Dict, Literal, Optional
from langchain_community.chat_models import ChatOllama

from langgraph.graph import add_messages
from operator import add
from typing import Annotated

class Msg(TypedDict):
    role: Literal["system","user","assistant","agent","supervisor"]
    name: Optional[str]
    content: str

class AgentState(TypedDict):
    name: str
    role_desc: str
    traits: Dict[str, str]
    long_mem: List[str]
    short_mem: List[Msg]
    agent_agenda: Dict[str, str]

class GraphState(TypedDict):
    messages: Annotated[List[Msg], add]
    agents: Dict[str, AgentState]
    round: int
    phase: Literal["debate","vote","interview","done"]
    #Reducer used here to accumulate notes
    supervisor_notes: Annotated[list[str], add]
    agenda: Dict[str, str]
    votes: Dict[str, str]
    models: Dict[str, ChatOllama]
    next_speaker: Optional[str]