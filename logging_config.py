import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    # Get the root logger
    logger = logging.getLogger()

    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Set the log level
    logger.setLevel(logging.INFO)

    # Define log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional: Add a file handler
    # file_handler = logging.FileHandler('bot.log')
    # file_handler.setLevel(logging.INFO)
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    # Prevent message propagation to the root logger
    logger.propagate = False
