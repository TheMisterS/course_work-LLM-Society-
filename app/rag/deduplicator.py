"""
RAG deduplicator - Step 4 of the persona persona creation pipeline.

Takes the raw list of Viewpoint objects extracted across all iterations
and removes duplicates in two phases:

  Phase A - rule-based: normalise source names and merge entries that
             resolve to the same key.
             
  Phase B - LLM-based (optional, RAG_DEDUP_USE_LLM=true): semantic pass
             that catches same-entity entries with differing name forms.
"""
import json
import logging
import re
from typing import List

from configs.rag_config import RAG_DEDUP_USE_LLM
from rag._llm import build_llm, call_llm, parse_json_list
from rag.state import Viewpoint

logger = logging.getLogger(__name__)

_PUNCT_RE = re.compile(r"[^\w\s]")

def _normalize_name(name: str) -> str:
    """Lowercase, strip punctuation, and collapse whitespace for key comparison."""
    name = name.lower()
    name = _PUNCT_RE.sub("", name)
    return " ".join(name.split())


def _dedup_llm_prompt(topic: str, viewpoints_json: str) -> dict:
    system_message = (
        "You are deduplicating a viewpoint list built to inform a debate simulation.\n"
        "Some entries may refer to the same actor under different name forms "
        "(e.g. an acronym vs. a full name, or a local vs. international name variant).\n\n"
        "Merge entries that clearly refer to the same entity:\n"
        "- Use the most complete / official source_name\n"
        "- Combine their key_arguments (deduplicate identical points)\n"
        "- Combine their sources\n"
        "- If stances conflict, set stance to 'mixed'\n\n"
        "Return the final deduplicated list as a JSON array using the same schema:\n"
        '  source_name, source_type, stance, key_arguments, sources\n'
        "Output ONLY valid JSON. No markdown fences. No explanation."
    )

    user_message = (
        f"Debate topic: {topic}\n\n"
        f"Viewpoint list:\n{viewpoints_json}"
    )

    return {"system_message": system_message, "user_message": user_message}


def _merge(existing: Viewpoint, incoming: Viewpoint) -> None:
    """Merge incoming into existing in-place."""

    # Keep the longer (more complete) name
    if len(incoming.get("source_name", "")) > len(existing.get("source_name", "")):
        existing["source_name"] = incoming["source_name"]

    # Combine arguments, drop exact duplicates, cap at 6
    all_args = existing.get("key_arguments", []) + incoming.get("key_arguments", [])
    existing["key_arguments"] = list(dict.fromkeys(all_args))[:6]

    # Combine source URLs, drop exact duplicates
    all_sources = existing.get("sources", []) + incoming.get("sources", [])
    existing["sources"] = list(dict.fromkeys(all_sources))

    # Resolve stance: unknown yields to any value; conflicting values → mixed
    existing_stance = existing.get("stance", "unknown")
    incoming_stance = incoming.get("stance", "unknown")
    if existing_stance == "unknown":
        existing["stance"] = incoming_stance
    elif incoming_stance not in ("unknown", existing_stance):
        existing["stance"] = "mixed"


def deduplicate(topic: str, viewpoints: List[Viewpoint]) -> List[Viewpoint]:
    """
    Deduplicate a list of Viewpoint objects.

    Phase A (always): rule-based merge
    Phase B (optional): LLM semantic merge when RAG_DEDUP_USE_LLM is True

    Args:
        topic: The debate topic (used as context for the LLM phase).
        viewpoints: Raw extracted viewpoints, possibly with duplicates.

    Returns:
        Deduplicated list of Viewpoint dicts.
    """
    logger.info("[deduplicator] input: %d viewpoints", len(viewpoints))

    # Phase A - rule-based
    merged: List[Viewpoint] = []
    seen: dict[str, int] = {}  # normalised_name → index in merged

    for vp in viewpoints:
        key = _normalize_name(vp.get("source_name", ""))
        if key in seen:
            _merge(merged[seen[key]], vp)
        else:
            seen[key] = len(merged)
            merged.append(dict(vp))

    logger.info("[deduplicator] after rule-based pass: %d viewpoints", len(merged))

    # Phase B - optional LLM merge
    if RAG_DEDUP_USE_LLM and len(merged) > 3:
        logger.info("[deduplicator] running LLM semantic dedup pass")
        try:
            llm = build_llm()
            prompts = _dedup_llm_prompt(
                topic=topic,
                viewpoints_json=json.dumps(merged, ensure_ascii=False, indent=2),
            )
            raw = call_llm(llm, prompts["system_message"], prompts["user_message"])
            parsed = parse_json_list(raw)
            if parsed:
                merged = parsed
                logger.info(
                    "[deduplicator] after LLM pass: %d viewpoints", len(merged)
                )
        except Exception as exc:
            logger.warning("[deduplicator] LLM dedup failed, keeping rule-based result: %s", exc)

    logger.info("[deduplicator] final viewpoint count: %d", len(merged))
    return merged
