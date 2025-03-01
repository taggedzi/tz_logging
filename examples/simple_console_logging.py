import sys
import logging
from tz_logging.core import TzLogger, StreamHandlerConfig

# Step 1: Initialize the logger with a blank configuration
logger_instance = TzLogger("simple_logger")

# Step 2: Create a basic console (stream) handler configuration
# - This will send log messages to standard output (console)
# - The log level is set to INFO (only INFO and higher messages will be shown)
console_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)

# Step 3: Add the console handler to the logger
logger_instance.add_stream_handler(console_config)

# Step 4: Log some sample messages to verify it works
logger_instance.logger.debug("This is a DEBUG message (will not be displayed since level is INFO).")
logger_instance.logger.info("This is an INFO message (should be displayed).")
logger_instance.logger.warning("This is a WARNING message (should be displayed).")
logger_instance.logger.error("This is an ERROR message (should be displayed).")
logger_instance.logger.critical("This is a CRITICAL message (should be displayed).")
