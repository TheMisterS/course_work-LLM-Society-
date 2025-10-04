

import os
from dotenv import load_dotenv

load_dotenv()


# General agenda items
DEBATE_TOPIC = os.environ.get("DEBATE_TOPIC", "The impact of artificial intelligence on society.")


# 
MODEL_USED_FOR_AGENTS = os.environ.get("MODEL_USED_FOR_AGENTS", "model_1")  # e.g., "model_1", "model_2"

#
DEBATE_ROUND_COUNT = int(os.environ.get("DEBATE_ROUND_COUNT", 10))