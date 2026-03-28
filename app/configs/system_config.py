
import os
import logging
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.environ.get("APP_ENV_FILE", ".env"))

LOG_FILE = os.environ.get("LOG_FILE", "app.log")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL, logging.DEBUG)





