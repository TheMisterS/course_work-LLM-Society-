"""
Stance-based viewpoint selector - Step 5a of persona creation pipeline.
"""
import logging
from typing import List

from configs.rag_config import PERSONA_STANCE_SCHEMA
from rag.state import Viewpoint

logger = logging.getLogger(__name__)


def _score(viewpoint: Viewpoint) -> int:
    
    """Score a viewpoint for selection priority based of number of arguments and sources"""
    return len(viewpoint.get("key_arguments", [])) * 2 + len(viewpoint.get("sources", []))


def select_by_stance(viewpoints: List[Viewpoint]) -> List[Viewpoint]:
    """
    Select viewpoints from the deduplicated pool according to PERSONA_STANCE_SCHEMA.

    Groups viewpoints by stance bucket (support, oppose, neutral/mixed), scores each candidate by argument richness, and picks the top N per bucket as defined in config.

    Args:
        viewpoints: Deduplicated list of Viewpoint dicts from the RAG pipeline.

    Returns:
        Selected subset of viewpoints respecting the configured stance distribution.
    """
    buckets: dict[str, List[Viewpoint]] = {
        "support": [],
        "oppose": [],
        "neutral": [],
        "unknown": [],
    }

    for vp in viewpoints:
        stance = vp.get("stance", "unknown").lower()
        if stance == "support":
            buckets["support"].append(vp)
        elif stance == "oppose":
            buckets["oppose"].append(vp)
        elif stance in ("neutral", "mixed"):
            buckets["neutral"].append(vp)
        else:
            buckets["unknown"].append(vp)

    selected: List[Viewpoint] = []

    for bucket_name, quota in PERSONA_STANCE_SCHEMA.items():
        candidates = sorted(buckets.get(bucket_name, []), key=_score, reverse=True)
        picked = candidates[:quota]

        if len(picked) < quota:
            logger.warning(
                "[stance_selector] bucket '%s' underfilled: wanted %d, got %d",
                bucket_name, quota, len(picked),
            )

        selected.extend(picked)
        logger.info(
            "[stance_selector] bucket '%s': selected %d / %d candidates",
            bucket_name, len(picked), len(candidates),
        )

    logger.info("[stance_selector] total selected: %d viewpoints", len(selected))
    return selected
