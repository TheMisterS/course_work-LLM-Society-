"""
Model configurations for different LLMs for within the same simulation.
Example 1:
MODEL_1 is used for agents speaking, MODEL_2 is used for supervisor/guardrailing
Example 2:
MODEL_1 is used for agent group A, MODEL_2 is used for agent group B
etc...

If you wish to test against different models on the same simulation, it should come as different .env files, not here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

def _int_or_none(key: str) -> int | None:
    v = os.environ.get(key)
    return int(v) if v is not None else None

MODEL_PROFILES = {
    "model_1": {
        # provider: ollama | openai | openrouter
        "provider": os.environ.get("MODEL_1_PROVIDER", "ollama"),
        "model": os.environ.get("MODEL_1_MODEL", "llama3.1:8b"),
        "temperature": float(os.environ.get("MODEL_1_TEMPERATURE", 0.9)),
        # Ollama-specific
        "top_p": float(os.environ.get("MODEL_1_TOP_P", 0.9)),
        "top_k": int(os.environ.get("MODEL_1_TOP_K", 40)),
        "num_ctx": int(os.environ.get("MODEL_1_NUM_CTX", 4096)),
        "num_predict": int(os.environ.get("MODEL_1_NUM_PREDICT", -1)),
        "repeat_penalty": float(os.environ.get("MODEL_1_REPEAT_PENALTY", 1.1)),
        # Remote API (open ai api)
        "api_key": os.environ.get("MODEL_1_API_KEY"),
        "base_url": os.environ.get("MODEL_1_BASE_URL"),
        "max_tokens": _int_or_none("MODEL_1_MAX_TOKENS"),
    }
    # Add more model configurations as needed
}