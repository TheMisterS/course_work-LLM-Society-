"""
RAG persona creation pipeline.

Orchestrates the full iterative loop:
  1. Plan queries  (query_planner)
  2. Search web    (search_tool)
  3. Extract viewpoints (extractor)
  4. Repeat until threshold met or max iterations reached
  5. Deduplicate   (deduplicator)
  6. Map each viewpoint directly to a GeneratedPersona
"""
import logging
from typing import List

from configs.rag_config import RAG_MAX_ITERATIONS, RAG_MIN_VIEWPOINTS
from rag.deduplicator import deduplicate
from rag.extractor import extract_viewpoints
from rag.query_planner import plan_queries
from rag.search_tool import execute_queries
from rag.state import GeneratedPersona, Viewpoint

logger = logging.getLogger(__name__)


def _viewpoint_to_persona(viewpoint: Viewpoint) -> GeneratedPersona:
    """Map a deduplicated Viewpoint directly to a GeneratedPersona."""
    return GeneratedPersona(
        name=viewpoint.get("source_name", "Unknown"),
        role_desc="",
        keypoints=viewpoint.get("key_arguments", []),
        background="",
    )


def build_persona_context(topic: str) -> List[GeneratedPersona]:
    """
    Run the full RAG pipeline for a debate topic and return one GeneratedPersona per stakeholder.

    Args:
        topic: The debate topic (typically DEBATE_TOPIC from config).
    """
    logger.info("[pipeline] starting RAG persona creation for topic: %s", topic)

    all_viewpoints: List[Viewpoint] = []
    all_queries: List[str] = []

    for iteration in range(1, RAG_MAX_ITERATIONS + 1):
        logger.info("[pipeline] iteration %d / %d", iteration, RAG_MAX_ITERATIONS)

        queries = plan_queries(topic, prior_queries=all_queries, iteration=iteration)
        all_queries.extend(queries)

        results = execute_queries(queries)
        if not results:
            logger.warning("[pipeline] iteration %d returned no search results", iteration)

        viewpoints, errors = extract_viewpoints(topic, results)
        if errors:
            logger.warning("[pipeline] iteration %d extraction errors: %s", iteration, errors)
        all_viewpoints.extend(viewpoints)

        logger.info(
            "[pipeline] iteration %d complete: +%d viewpoints (total: %d)",
            iteration, len(viewpoints), len(all_viewpoints),
        )

        if len(all_viewpoints) >= RAG_MIN_VIEWPOINTS:
            logger.info("[pipeline] threshold reached - stopping early at iteration %d", iteration)
            break

    if not all_viewpoints:
        raise RuntimeError(
            f"[pipeline] no viewpoints extracted after {RAG_MAX_ITERATIONS} iteration(s) "
            f"for topic: '{topic}'. Check API keys, network access, and search config."
        )

    final_viewpoints = deduplicate(topic, all_viewpoints)
    personas = [_viewpoint_to_persona(vp) for vp in final_viewpoints]

    logger.info("[pipeline] created %d personas from RAG viewpoints", len(personas))
    return personas
