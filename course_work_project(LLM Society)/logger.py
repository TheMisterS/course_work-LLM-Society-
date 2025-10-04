import logging
from configs.system_config import LOG_FILE

def setup_logger(log_level=logging.DEBUG, log_file=LOG_FILE):
    """Configure root logger."""

    logging.basicConfig(
        level=logging.DEBUG,  # or INFO
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )