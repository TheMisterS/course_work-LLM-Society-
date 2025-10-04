from configs.models_config import MODEL_PROFILES, OLLAMA_URL
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import logging
logger = logging.getLogger(__name__)

def configure_model(model_kwargs=MODEL_PROFILES, base_url=OLLAMA_URL):
    if not MODEL_PROFILES:
        logger.error("MODEL_KWARGS is not defined.")
    logger.debug(f"Creating ChatOllama model with model  {model_kwargs["model"]}")

    model = ChatOllama(**model_kwargs)
    return model


def create_agent_chain(model):
    logger.debug("Creating agent chain with provided prompts.")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_message}"),
        ("user", "{user_message}")
    ])

    chain = prompt | model | StrOutputParser()
    #(WIP) might need to decide if a parser is needed or opperate with pure messages?
    return chain
