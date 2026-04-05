"""
Institutional background fetcher - Step 5b of persona creation pipeline.

Fetches background context for each selected viewpoint(persona) via plain keyword searches.
"""
import logging
import os
from typing import List

from langchain_tavily import TavilySearch

from configs.rag_config import (
    BACKGROUND_FETCHER_INCLUDE_DOMAINS,
    TAVILY_SEARCH_DEPTH,
    TAVILY_API_KEY,
)
from rag.search_tool import execute_query
from rag.state import Viewpoint

logger = logging.getLogger(__name__)

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

_fetch_tool = TavilySearch(
    max_results=2,
    search_depth=TAVILY_SEARCH_DEPTH,
    include_domains=BACKGROUND_FETCHER_INCLUDE_DOMAINS or None,
)

_MIN_CONTENT_LENGTH = 100
_MAX_CONTENT_LENGTH = 800


def fetch_backgrounds(viewpoints: List[Viewpoint], topic: str = "") -> List[Viewpoint]:
    """
    Fetch institutional background for every viewpoint(persona) via keyword searches.

    Queries are anchored with Lithuania and the stakeholder type to avoid wrong
    definitions for generic or ambiguous names

    Args:
        viewpoints: Selected viewpoints from stance_selector.
        topic: The debate topic — used in the fallback query for extra context.

    Returns:
        The same list with `_enrichment_raw` populated on each entry.
    """
    for vp in viewpoints:
        source_name = vp.get("source_name", "")
        source_type = vp.get("source_type", "")

        # Build a type hint for the query (e.g. "NGO", "government", "media")
        type_hint = f"{source_type} " if source_type and source_type != "other" else ""

        # Primary: Wikipedia-first
        topic_hint = f" {topic}" if topic else ""
        primary_query = f"{source_name} {type_hint}Lithuania{topic_hint} Wikipedia"
        primary_results = execute_query(_fetch_tool, primary_query)
        primary_content = "".join(r.get("content", "") for r in primary_results)

        if len(primary_content) >= _MIN_CONTENT_LENGTH:
            logger.info(
                "[background_fetcher] primary hit for %s - %d chars",
                source_name, len(primary_content),
            )
            vp["_enrichment_raw"] = primary_content[:_MAX_CONTENT_LENGTH]
            continue

        # Fallback: drop Wikipedia, just go with Lithuania
        logger.info("[background_fetcher] fallback triggered for %s", source_name)
        fallback_query = f"{source_name} {type_hint}Lithuania{topic_hint}"
        fallback_results = execute_query(_fetch_tool, fallback_query)
        fallback_content = "".join(r.get("content", "") for r in fallback_results)

        if len(fallback_content) >= _MIN_CONTENT_LENGTH:
            vp["_enrichment_raw"] = fallback_content[:_MAX_CONTENT_LENGTH]
        else:
            logger.warning("[background_fetcher] no content found for %s", source_name)
            vp["_enrichment_raw"] = ""

    return viewpoints
