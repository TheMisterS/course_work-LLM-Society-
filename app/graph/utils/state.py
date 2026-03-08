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
    models: Dict[str, ChatOllama]
    next_speaker: Optional[str]
    votes: Dict[str, str]  # agent_name -> vote_choice
    voting_options: List[str]  # Available options to vote on
    voting_question: str  # The question being voted on

class IndividualPersona(TypedDict):
    demographics: Dict[str, str]  # e.g. age, gender, education, occupation ...

class IndividualState(TypedDict):
    persona: IndividualPersona
    questions: List[str]
    current_question_index: int
    messages: Annotated[List[Msg], add]
    phase: Literal["individual","done"]
    models: Dict[str, ChatOllama]