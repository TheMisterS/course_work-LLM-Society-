"""
RAG query planner - Step 1 of the persona pre-loading pipeline.

Given a debate topic, calls an LLM to produce a list of Tavily-ready search queries
"""
import logging
from typing import List

from configs.rag_config import RAG_QUERY_COUNT
from rag._llm import build_llm, call_llm, parse_json_list

logger = logging.getLogger(__name__)

def _plan_queries_prompt(
    topic: str,
    query_count: int,
    prior_queries: List[str],
    iteration: int,
) -> dict:
    
    prior_instruction = ""
    
    if iteration > 1 and prior_queries:
        prior_list = "\n".join(f"- {q}" for q in prior_queries)
        
        prior_instruction = (
            f"\nThese queries were already searched - do NOT repeat them:\n{prior_list}\n"
            "Generate queries that target different sources or aspects of the topic."
        )

    system_message = (
        "You are a research assistant. Generate precise, neutral web search queries to find "
        "information, stakeholders, and sources related to the given topic.\n"
        "Write queries as a person would type them into a search engine - factual and concise, "
        "without analytical framing (do NOT embed words like 'proponents', 'opponents', "
        "'impact of', or 'concerns about' into the queries).\n"
        f"{prior_instruction}\n\n"
        "Output format: return ONLY a JSON array of strings. No explanation, no markdown fences.\n"
        'Example: ["query 1", "query 2", "query 3"]'
    )

    user_message = (
        f"Topic: {topic}\n"
        f"Generate exactly {query_count} search queries."
    )

    return {"system_message": system_message, "user_message": user_message}

def plan_queries(
    topic: str,
    prior_queries: List[str] | None = None,
    iteration: int = 1,
    query_count: int = RAG_QUERY_COUNT,
) -> List[str]:
    """
    Return a list of search query strings for the given debate topic.

    Args:
        topic: The debate topic (from DEBATE_TOPIC config).
        prior_queries: Queries already executed in previous iterations.
        iteration: Current iteration number (1-based).
        query_count: Number of queries to generate.

    Returns:
        List of query strings.
    """
    prior_queries = prior_queries or []
    logger.info("[query_planner] iteration=%d, generating %d queries", iteration, query_count)

    llm = build_llm()
    prompts = _plan_queries_prompt(topic, query_count, prior_queries, iteration)
    raw = call_llm(llm, prompts["system_message"], prompts["user_message"])
    logger.debug("[query_planner] raw LLM output: %s", raw)

    # First try to parse as JSON list. If that fails, fall back to line-splitting.
    try:
        queries = [str(q) for q in parse_json_list(raw)]
    except Exception as exc:
        logger.warning("[query_planner] JSON parse failed (%s), falling back to line split", exc)
        queries = [
            line.strip().strip('"').strip("'")
            for line in raw.splitlines()
            if line.strip()
        ]

    logger.info("[query_planner] produced queries: %s", queries)
    return queries
