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
    _enrichment_raw: str      # populated by background_fetcher; absent until that step runs

class GeneratedPersona(TypedDict):
    name: str                 # human first name
    affiliation: str          # organisation or individual being represented, e.g. "LRT" or "Valdas Benkunskas"
    role_desc: str            #  2-3 sentence persona description
    keypoints: List[str]
    background: str           # 1-2 sentence context from enrichment
    stance: str               # carried over from Viewpoint: support|oppose|neutral|mixed
    sources: List[str]        # URLs where this persona's views were found (from the Viewpoint.sources)
