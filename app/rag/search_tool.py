"""
RAG search tool - Step 2 of the persona creation pipeline.

Builds Tavily search tool using config values, then runs each query and returns a list of SearchResult dicts.
"""
import os
import logging
from typing import List
from langchain_tavily import TavilySearch
from configs.rag_config import (
    TAVILY_API_KEY,
    TAVILY_INCLUDE_DOMAINS,
    TAVILY_MAX_RESULTS,
    TAVILY_SEARCH_DEPTH,
)

from rag.state import SearchResult

logger = logging.getLogger(__name__)

# LangChain needs to read the Tavily key from the environment
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

def build_search_tool() -> TavilySearch:
    """Instantiate and return a configured TavilySearch tool."""
    return TavilySearch(
        max_results=TAVILY_MAX_RESULTS,
        search_depth=TAVILY_SEARCH_DEPTH,
        include_domains=TAVILY_INCLUDE_DOMAINS or None,
    )


def execute_query(tool: TavilySearch, query: str) -> List[SearchResult]:
    """
    Run a single query and return a list of SearchResult dicts.
    Returns an empty list on error so the pipeline can continue gracefully.
    """
    try:
        raw = tool.invoke(query)

        # [WIP!] TavilySearch returns {"query": ..., "results": [...], ...}
        items = raw.get("results", []) if isinstance(raw, dict) else raw

        results: List[SearchResult] = []

        for item in items:
            
            # discard score, title, (optional answer, will not be used during bachelors) and other extras.
            result = SearchResult(
                query=query,
                content=item.get("content", ""),
                url=item.get("url", ""),
            )
            results.append(result)
        
        logger.debug("[search_tool] query='%s' → %d results", query, len(results))
        return results
    
    except Exception as exc:
        logger.warning("[search_tool] query failed ('%s'): %s", query, exc)
        return []


def execute_queries(queries: List[str]) -> List[SearchResult]:
    """
    Execute all queries in a sequence using a single shared tool.
    """
    tool = build_search_tool()
    results: List[SearchResult] = []
    
    for query in queries:
        results.extend(execute_query(tool, query))
        
    logger.info("[search_tool] %d queries → %d total results", len(queries), len(results))
    
    return results
