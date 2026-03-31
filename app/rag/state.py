"""
Shared TypedDict definitions for the RAG persona pre-loading pipeline.
"""
from typing import TypedDict, List, Dict

# Maps to Tavily search results with only the fields that are needed for RAG
class SearchResult(TypedDict):
    query: str
    content: str
    url: str


class Viewpoint(TypedDict):
    source_name: str          # name of the actor / stakeholder
    source_type: str          # government | ngo | business | academic | media | other
    stance: str               # support | oppose | neutral | mixed | unknown
    key_arguments: List[str]  # 2-4 strings summarising their position
    sources: List[str]        # URLs where this viewpoint was found

class GeneratedPersona(TypedDict):
    name: str
    role_desc: str
    keypoints: List[str]
    background: str
