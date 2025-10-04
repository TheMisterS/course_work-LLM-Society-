
import os
import logging
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = os.environ.get("LOG_FILE", "app.log")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL, logging.DEBUG)





