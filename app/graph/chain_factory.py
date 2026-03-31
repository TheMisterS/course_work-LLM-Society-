from configs.models_config import MODEL_PROFILES, configure_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import logging
logger = logging.getLogger(__name__)


def create_agent_chain(model):
    logger.debug("Creating agent chain with provided prompts.")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_message}"),
        ("user", "{user_message}")
    ])
    chain = prompt | model | StrOutputParser()
    return chain
