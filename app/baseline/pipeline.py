import json
import logging
import os
from typing import List

from baseline.prompts import BASELINE_SYSTEM_PROMPT, build_baseline_user_message
from configs.rag_config import PERSONA_STANCE_SCHEMA, RAG_MIN_VIEWPOINTS, SYNTHESIS_MAX_RETRIES
from configs.models_config import MODEL_PROFILES, configure_model
from rag._llm import call_llm, parse_json_list
from rag.persona_synthesis import _LITHUANIAN_NAMES
from rag.state import GeneratedPersona

logger = logging.getLogger(__name__)

def build_persona_context_no_rag(topic: str, output_dir: str | None = None) -> List[GeneratedPersona]:
    logger.info("[baseline] generating personas from general knowledge for topic: %s", topic)

    llm = configure_model(MODEL_PROFILES["baseline"])
    user_message = build_baseline_user_message(topic, PERSONA_STANCE_SCHEMA, RAG_MIN_VIEWPOINTS)

    # retry loop in case the llm outputs malformed json
    raw_response = None
    items = None

    for attempt in range(1, SYNTHESIS_MAX_RETRIES + 1):
        try:
            raw_response = call_llm(llm, BASELINE_SYSTEM_PROMPT, user_message)
            items = parse_json_list(raw_response)
            break
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning(
                "[baseline] attempt %d/%d failed to parse response: %s",
                attempt, SYNTHESIS_MAX_RETRIES, exc,
            )

    if items is None:
        raise RuntimeError(
            f"[baseline] failed to parse LLM response after {SYNTHESIS_MAX_RETRIES} attempts. "
            f"Last raw response: {raw_response!r}"
        )

    personas: List[GeneratedPersona] = []

    for i, item in enumerate(items):
        name = _LITHUANIAN_NAMES[i % len(_LITHUANIAN_NAMES)]

        persona = GeneratedPersona(
            name=name,
            affiliation=item.get("affiliation", ""),
            role_desc=item.get("role_desc", ""),
            keypoints=item.get("keypoints", []),
            background=item.get("background", ""),
            stance=item.get("stance", ""),
            sources=["general knowledge"],
        )

        logger.info(
            "[baseline] persona '%s' → '%s' [%s]",
            name, persona["affiliation"], persona["stance"],
        )
        personas.append(persona)

    # write to the same path as rag so vote evaluation can find personas
    if output_dir:
        rag_dir = os.path.join(output_dir, "rag")
        os.makedirs(rag_dir, exist_ok=True)

        personas_path = os.path.join(rag_dir, "07_personas.json")
        with open(personas_path, "w", encoding="utf-8") as f:
            json.dump({"total": len(personas), "personas": list(personas)}, f, ensure_ascii=False, indent=2)

        logger.info("[baseline] saved personas to %s", personas_path)

    logger.info("[baseline] created %d personas from general knowledge", len(personas))
    return personas
