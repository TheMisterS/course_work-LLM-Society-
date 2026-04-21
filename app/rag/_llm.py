"""
Shared LLM utilities for the RAG persona creation pipeline.
"""
import json
import logging

from langchain_core.messages import SystemMessage, HumanMessage

from configs.models_config import MODEL_PROFILES, configure_model

logger = logging.getLogger(__name__)


def build_llm():
    """Instantiate the RAG LLM from the RAG model profile."""
    return configure_model(MODEL_PROFILES["rag"])


def call_llm(llm, system_message: str, user_message: str) -> str:
    """Send a system + user message pair and return the response text."""
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=user_message),
    ]
    return llm.invoke(messages).content


def strip_json_fences(text: str) -> str:
    """Strip markdown code fences (```json ... ``` or ``` ... ```) from an LLM response."""
    cleaned = text.strip()

    # Fast path for unfenced output.
    if not cleaned.startswith("```"):
        return cleaned

    lines = cleaned.splitlines()

    if not lines:
        return cleaned

    opening_fence = lines[0].strip().lower()
    if opening_fence in {"```", "```json"}:
        lines = lines[1:]

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


def parse_json_list(text: str) -> list:
    """Strip markdown fences and parse a JSON array from an LLM response."""
    result = json.loads(strip_json_fences(text))
    
    if not isinstance(result, list):
        raise ValueError(f"Expected a JSON array, got {type(result).__name__}")
    return result


def parse_json_object(text: str) -> dict:
    """Strip markdown fences and parse a JSON object from an LLM response."""
    result = json.loads(strip_json_fences(text))
    
    if not isinstance(result, dict):
        raise ValueError(f"Expected a JSON object, got {type(result).__name__}")
    return result
