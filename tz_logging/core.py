"""
Module providing the ability to save a new file to a specified path with a string input.
"""
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import TextIO


LOGGER_NAME = 'tz_logger'
LOGGER_OUTPUT_FORMAT_LONG = '\n'.join([
    '------------------------------------',
    '   Logging Level: %(levelname)s',
    ' - Time:          %(asctime)s',
    ' - File:          %(pathname)s',
    ' - Function:      %(funcName)s',
    ' - Line Number:   %(lineno)d',
    ' - Message:       %(message)s',
    '------------------------------------'
])
LOGGER_OUTPUT_FORMAT = '\n'.join([
    '[%(levelname)s] %(asctime)s',
    '[%(pathname)s] %(funcName)s Line: %(lineno)d',
    '%(message)s'
])
LOGGER_OUTPUT_FORMAT_SHORT = '\n'.join([
    '[%(levelname)s] %(asctime)s:  %(message)s'
])



# Create or get the logger
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)

def add_file_handler(file_path:str = None, max_bytes:int = 10*1024*1024, backup_count:int = 5, level: int = logging.DEBUG): # type: ignore
    """
    Adds a rotating file handler to the logger.

    Parameters:
        file_path (str): Path to the log file.
        max_bytes (int): Maximum file size in bytes before rotation (default: 10 MB).
        backup_count (int): Number of backup files to keep (default: 5).
        level: Logging level for the handler.
    """
    rotating_handler = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
    rotating_handler.setLevel(level)
    formatter = logging.Formatter(LOGGER_OUTPUT_FORMAT)
    rotating_handler.setFormatter(formatter)
    logger.addHandler(rotating_handler)


def add_stream_handler(stream: TextIO = sys.stdout, level: int = logging.INFO):
    """
    Adds a configurable stream handler to the logger.
    
    Parameters:
        stream: The output destination (e.g., sys.stdout, sys.stderr or any file-like object).
        level: Logging level for the stream handler (e.g., logging.INFO, logging.DEBUG).
    """
    stream_handler = logging.StreamHandler(stream)
    stream_handler.setLevel(level)
    new_formatter = logging.Formatter(LOGGER_OUTPUT_FORMAT)
    stream_handler.setFormatter(new_formatter)
    logger.addHandler(stream_handler)


class CustomFilter(logging.Filter):
    """ This is a simple sample class to demonstrate how to create and implement
        custom filtering for logging in python. This requiers that the filter be
        registerd with each logging handler you wish to use the filter on.
        See the example in the __main__ section below. """
    def filter(self, record):
        # Example: Only log messages that do NOT contain the word "ignore"
        return "ignore" not in record.getMessage()


if __name__ == "__main__":
    # Example configuration for when running the module

    # Optional: add a file handler if file logging is desired.
    add_file_handler("txt2md_logger.log", level=logging.DEBUG)
    
    # Add a stream handler to output INFO level and above messages to stdout.
    add_stream_handler(sys.stdout, level=logging.INFO)
    
    # Log some messages to demonstrate the configuration.
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")

    # Add the custom filter to a handler
    for handler in logger.handlers:
        handler.addFilter(CustomFilter())

     # Log some messages to demonstrate the configuration.
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message to ignore.")
    logger.error("This is an error message.")
