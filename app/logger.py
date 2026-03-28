import logging
import sys
import colorlog

from configs.system_config import LOG_FILE, LOG_LEVEL

def setup_logger(log_level=LOG_LEVEL, log_file=LOG_FILE):
    """Configure root logger."""

    # Ensure Windows console can print UTF-8 characters from prompts and personas.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(log_level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Keep third-party HTTP/client libraries quieter unless explicitly overridden.
    for noisy_logger in ("openai", "httpx", "httpcore"):
        logging.getLogger(noisy_logger).setLevel(max(log_level, logging.INFO))