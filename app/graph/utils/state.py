from typing import TypedDict, List, Dict, Literal, Optional, Any
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
    keypoints: List[str]
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
    models: Dict[str, ChatOllama]
    next_speaker: Optional[str]
    # {"initial": {agent: {"vote": str, "reason": str}}, "mid": {...}, "final": {...}}`
    votes: Dict[str, Any]
    voting_options: List[str]
    voting_question: str
    # set by supervisor before entering vote node so the node knows which round to write under -> initial/mid/final
    current_vote_label: Optional[str]
    # tracks the round when long-mem node ran last to prevent double updating during voting
    last_long_mem_update_round: int