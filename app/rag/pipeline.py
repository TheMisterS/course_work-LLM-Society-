"""
RAG persona creation pipeline.

Orchestrates the full iterative loop:
  1. Plan queries       (query_planner)
  2. Search web         (search_tool)
  3. Extract viewpoints (extractor)
  4. Repeat until threshold met or max iterations reached
  5. Deduplicate        (deduplicator)
  6. Select by stance   (stance_selector)
  7. Fetch backgrounds  (background_fetcher)
  8. Synthesize personas (persona_synthesis)
"""
import logging
from typing import List

from configs.rag_config import RAG_MAX_ITERATIONS, RAG_MIN_VIEWPOINTS
from rag.background_fetcher import fetch_backgrounds
from rag.deduplicator import deduplicate
from rag.extractor import extract_viewpoints
from rag.persona_synthesis import synthesize_personas
from rag.query_planner import plan_queries
from rag.search_tool import execute_queries
from rag.stance_selector import select_by_stance
from rag.state import GeneratedPersona, Viewpoint
from rag.rag_logger import RagRunLogger

logger = logging.getLogger(__name__)


def build_persona_context(topic: str, output_dir: str | None = None) -> List[GeneratedPersona]:
    """
    Run the full RAG pipeline for a debate topic and return one GeneratedPersona per stakeholder.

    Args:
        topic: The debate topic (typically DEBATE_TOPIC from config).
        output_dir: Optional subsession folder path. When provided, each pipeline stage writes
            a JSON log under output_dir/rag/. When omitted, no stage logs are written.
    """
    logger.info("[pipeline] starting RAG persona creation for topic: %s", topic)

    rag_log = None
    if output_dir:
        rag_log = RagRunLogger(output_dir)

    all_viewpoints: List[Viewpoint] = []
    all_queries: List[str] = []

    for iteration in range(1, RAG_MAX_ITERATIONS + 1):
        logger.info("[pipeline] iteration %d / %d", iteration, RAG_MAX_ITERATIONS)

        queries = plan_queries(topic, prior_queries=all_queries, iteration=iteration)
        all_queries.extend(queries)
        if rag_log:
            rag_log.log_queries(iteration, queries)

        results = execute_queries(queries)
        if not results:
            logger.warning("[pipeline] iteration %d returned no search results", iteration)
        if rag_log:
            rag_log.log_search_results(iteration, results)

        viewpoints, errors = extract_viewpoints(topic, results)
        if errors:
            logger.warning("[pipeline] iteration %d extraction errors: %s", iteration, errors)
        all_viewpoints.extend(viewpoints)
        if rag_log:
            rag_log.log_viewpoints_raw(viewpoints, errors)

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
    if rag_log:
        rag_log.log_viewpoints_deduped(len(all_viewpoints), len(final_viewpoints), final_viewpoints)

    selected = select_by_stance(final_viewpoints)
    if rag_log:
        rag_log.log_viewpoints_selected(selected)

    enriched = fetch_backgrounds(selected, topic=topic)
    if rag_log:
        rag_log.log_viewpoints_enriched(enriched)

    personas = synthesize_personas(topic, enriched)
    if rag_log:
        rag_log.log_personas(personas)

    logger.info("[pipeline] created %d personas from RAG viewpoints", len(personas))
    return personas
