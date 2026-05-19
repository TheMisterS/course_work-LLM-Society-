"""
RAG viewpoint extractor - Step 3 of the persona creation pipeline.

Takes a batch of  SearchResult dicts and calls an OpenRouter LLM to
extract structured Viewpoint objects (actors, their stance, and key arguments).
"""
import logging
from typing import List, Tuple

from rag._llm import build_llm, call_llm, parse_json_list
from rag.state import SearchResult, Viewpoint

logger = logging.getLogger(__name__)

_BATCH_SIZE = 3  #[WIP] search results to process per LLM call -> should be moved to config

def _extract_viewpoints_prompt(topic: str, formatted_results: str) -> dict:
    system_message = (
        "You are an analyst helping to build background knowledge for a debate simulation.\n"
        "Extract all distinct viewpoints expressed in the provided search results that are "
        "relevant to the debate topic.\n\n"
        "A viewpoint     is held by any organisation, institution, expert, or named group that:\n"
        "- Has expressed a position (for / against / neutral) on the topic, OR\n"
        "- Has material interests affected by the topic, OR\n"
        "- Has regulatory or policy authority over the topic.\n\n"
        "For each viewpoint output a JSON array of objects with EXACTLY these keys:\n"
        '- "source_name": the most specific known name of the actor or organisation '
        '(e.g. "Lithuanian Ministry of Finance" not "the government", '
        '"Vilnius City Municipality" not "local authorities")\n'
        '- "source_type": one of [government, ngo, business, academic, media, other]\n'
        '- "stance": one of [support, oppose, neutral]\n'
        '- "key_arguments": list of 2-4 concise declarative sentences, each capturing '
        'one distinct argument, concern, or interest this actor holds regarding the topic\n'
        '- "sources": list of URLs where this viewpoint was found\n\n'
        "Output ONLY valid JSON. No markdown fences. No explanation.\n"
        "If no viewpoints are found, output: []"
    )

    user_message = (
        f"Debate topic: {topic}\n\n"
        f"Search results:\n---\n{formatted_results}\n---\n\n"
        "Extract all viewpoints from the above text."
    )

    return {"system_message": system_message, "user_message": user_message}


def extract_viewpoints(
    topic: str,
    results: List[SearchResult],
) -> Tuple[List[Viewpoint], List[str]]:
    """
    Extract structured Viewpoint objects from a list of SearchResult dicts.

    Processes results in batches of 3 to keep token usage per call bounded.

    Args:
        topic:   The debate topic used as context for the LLM.
        results: Raw search results from search_tool.execute_queries().

    Returns:
        A tuple of (viewpoints, errors) where errors is a list of failure
        messages for any batch that could not be parsed.
    """
    llm = build_llm()
    viewpoints: List[Viewpoint] = []
    errors: List[str] = []

    for i in range(0, len(results), _BATCH_SIZE):
        
        batch = results[i : i + _BATCH_SIZE]
        
        formatted = ""
        for result in batch:
            formatted += f"[Source: {result['url']}]\n{result['content']}\n\n"
        
        # remove newlines from the final string
        formatted = formatted.strip()

        prompts = _extract_viewpoints_prompt(topic, formatted)

        try:
            raw = call_llm(llm, prompts["system_message"], prompts["user_message"])
            logger.debug("[extractor] batch %d raw: %s", i // _BATCH_SIZE, raw[:300])
            
            parsed = parse_json_list(raw)
            viewpoints.extend(parsed)
            
            logger.info(
                "[extractor] batch %d → %d viewpoints", i // _BATCH_SIZE, len(parsed)
            )
            
        except Exception as exc:
            msg = f"Extraction failed for batch {i // _BATCH_SIZE}: {exc}"
            logger.warning("[extractor] %s", msg)
            errors.append(msg)

    logger.info("[extractor] total viewpoints extracted: %d", len(viewpoints))
    return viewpoints, errors
