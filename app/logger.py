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
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)