"""
Model configuration for both the discussion graph and the RAG pipeline.

Provider options per profile:
  "ollama" - local Ollama instance (ChatOllama in langGraph)
  "openrouter" - OpenRouter API (ChatOpenAI in langGraph, with custom base_url)
"""
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI


load_dotenv()

OLLAMA_URL          = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OPENROUTER_API_KEY  = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

MODEL_PROFILES = {
    # --- Discussion models ---
    "model_1": {
        "provider":       os.environ.get("MODEL_1_PROVIDER", "ollama"),  # ollama | openrouter
        "model":          os.environ.get("MODEL_1_MODEL", "llama3.1:8b"),
        "temperature":    float(os.environ.get("MODEL_1_TEMPERATURE", 0.7)),
        # Ollama-specific
        "top_p":          float(os.environ.get("MODEL_1_TOP_P", 0.9)),
        "top_k":          int(os.environ.get("MODEL_1_TOP_K", 40)),
        "num_ctx":        int(os.environ.get("MODEL_1_NUM_CTX", 4096)),
        "num_predict":    int(os.environ.get("MODEL_1_NUM_PREDICT", -1)),
        "repeat_penalty": float(os.environ.get("MODEL_1_REPEAT_PENALTY", 1.1)),
        # OpenRouter-specific
        "max_tokens":     int(os.environ.get("MODEL_1_MAX_TOKENS", 4096)),
    },
    # --- RAG pipeline model ---
    "rag": {
        "provider":    os.environ.get("RAG_MODEL_PROVIDER", "openrouter"),  # ollama | openrouter
        "model":       os.environ.get("RAG_MODEL", "openai/gpt-4o-mini"),
        "temperature": float(os.environ.get("RAG_MODEL_TEMPERATURE", 0.1)),
        "max_tokens":  int(os.environ.get("RAG_MODEL_MAX_TOKENS", 4096)),
    },
}

_OLLAMA_KEYS = {"model", "temperature", "top_p", "top_k", "num_ctx", "num_predict", "repeat_penalty"}
_OPENROUTER_KEYS = {"model", "temperature", "max_tokens"}


def configure_model(profile: dict):
    """
    Instantiate the correct LangChain chat model from a MODEL_PROFILES entry.

    Returns ChatOllama for provider="ollama", ChatOpenAI for provider="openrouter".
    """
    provider = profile.get("provider", "ollama")

    if provider == "openrouter":
        kwargs = {k: profile[k] for k in _OPENROUTER_KEYS if k in profile}
        return ChatOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            **kwargs,
        )
    else: # default to ollama
        kwargs = {k: profile[k] for k in _OLLAMA_KEYS if k in profile}
        return ChatOllama(base_url=OLLAMA_URL, **kwargs)
