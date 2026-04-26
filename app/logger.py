import logging
import colorlog

from configs.system_config import LOG_FILE, LOG_LEVEL

def setup_logger(log_level=LOG_LEVEL, log_file=LOG_FILE):
    """Configure root logger."""

    # colored formatter for console
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    # standard formatter for file
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    console_handler.setLevel(log_level)
    file_handler.setLevel(log_level)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # suppress annoying third-party library loggers
    for annoying in ("openai", "httpx", "httpcore", "urllib3"):
        logging.getLogger(annoying).setLevel(logging.WARNING)