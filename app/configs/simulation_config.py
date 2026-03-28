

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.environ.get("APP_ENV_FILE", ".env"))

# General agenda items
DEBATE_TOPIC = os.environ.get("DEBATE_TOPIC", """The impact of artificial intelligence on society?""")

#Voting configuration
VOTING_QUESTION = os.environ.get("VOTING_QUESTION", "Based on the debate, what is your final position on the topic? Do you think the impact of artificial intelligence on society is overall positive?")

VOTING_OPTIONS = os.environ.get("VOTING_OPTIONS", "Strongly For,For,Neutral,Against,Strongly Against").split(",")
VOTING_OPTIONS = [option.strip() for option in VOTING_OPTIONS]

# Model configuration
MODEL_USED_FOR_DEBATE = os.environ.get("MODEL_USED_FOR_DEBATE", "model_1")  # e.g., "model_1", "model_2"
MODEL_USED_FOR_VOTING = os.environ.get("MODEL_USED_FOR_VOTING", "model_1")

# Debate configuration
DEBATE_ROUND_COUNT = int(os.environ.get("DEBATE_ROUND_COUNT", 10)) # Total number of debate rounds before voting phase
MEMORY_WINDOW_SIZE = int(os.environ.get("MEMORY_WINDOW_SIZE", 5))  # Number of recent messages to retain in memory

# Long-term memory configuration
LONG_MEMORY_ENABLED = os.environ.get("LONG_MEMORY_ENABLED", "true").lower() == "true"  # Enable/disable long-term memory feature
LONG_MEMORY_UPDATE_INTERVAL = int(os.environ.get("LONG_MEMORY_UPDATE_INTERVAL", 5))  # Update long memory every N rounds
LONG_MEMORY_THRESHOLD_PERCENT = float(os.environ.get("LONG_MEMORY_THRESHOLD_PERCENT", 0.8))  # Trigger when short_mem is at least 80% full
MODEL_USED_FOR_SUMMARIZATION = os.environ.get("MODEL_USED_FOR_SUMMARIZATION", "model_1")  # Model used for memory summarization