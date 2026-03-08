from configs.models_config import MODEL_PROFILES, OLLAMA_URL

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import logging
logger = logging.getLogger(__name__)

_OLLAMA_KEYS = {"model", "temperature", "top_p", "top_k", "num_ctx", "num_predict", "repeat_penalty", "base_url"}
_OPENAI_KEYS = {"model", "temperature", "api_key", "base_url", "max_tokens"}

def configure_model(profile: dict):
    provider = profile.get("provider", "ollama")
    logger.debug(f"Configuring model — provider: {provider!r}, model: {profile.get('model')!r}")

    if provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        kwargs = {k: v for k, v in profile.items() if k in _OLLAMA_KEYS and v is not None}
        kwargs.setdefault("base_url", OLLAMA_URL)
        return ChatOllama(**kwargs)

    elif provider in ("openai", "openrouter"):
        from langchain_openai import ChatOpenAI
        kwargs = {k: v for k, v in profile.items() if k in _OPENAI_KEYS and v is not None}
        if provider == "openrouter":
            kwargs.setdefault("base_url", "https://openrouter.ai/api/v1")
        return ChatOpenAI(**kwargs)

    else:
        raise ValueError(f"Unknown provider {provider!r}. Supported: ollama, openai, openrouter")


def create_agent_chain(model):
    logger.debug("Creating agent chain with provided prompts.")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_message}"),
        ("user", "{user_message}")
    ])

    chain = prompt | model | StrOutputParser()
    #(WIP) might need to decide if a parser is needed or opperate with pure messages?
    return chain
