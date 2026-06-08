import logging
import os

def setup_logging(log_filename="trading_bot.log"):
    """
    Configures logging to print to console (clean format) and write to a file (detailed format).
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(os.path.abspath(log_filename))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Base configuration for root logger
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate logs if setup_logging is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler (detailed logs)
    file_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d]: %(message)s"
    )
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler (clean, user-friendly logs)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Get the logger instance
logger = logging.getLogger("trading_bot")
