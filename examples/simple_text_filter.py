import sys
import logging
from tz_logging.core import TzLogger, StreamHandlerConfig

# Initialize the logger
positive_filter = TzLogger("key_word_log")

# Step 2: Create a basic console (stream) handler configuration
# - This will send log messages to standard output (console)
# - The log level is set to INFO (only INFO and higher messages will be shown)
console_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)

# Step 3: Add a stream handler to print logs to the console
positive_filter.add_stream_handler(console_config)

# Step 4: Add a positive keyword filter (only logs with "CRITICAL FAILURE" will be shown)
positive_filter.add_keyword_filter("CRITICAL FAILURE", positive=True)

positive_filter.logger.info("This is an INFO message.")   # Will be filtered out
positive_filter.logger.error("This is an ERROR message.")  # Will be filtered out
positive_filter.logger.critical("This is a CRITICAL FAILURE message.")  # Will be shown
positive_filter.logger.critical("This is a CRITICAL message.")  # Will be filtered


# Initialize the logger
negative_filter = TzLogger("exclude_log")

# Step 2: Create a basic console (stream) handler configuration
# - This will send log messages to standard output (console)
# - The log level is set to INFO (only INFO and higher messages will be shown)
console_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)

# Step 3: Add a stream handler to print logs to the console
negative_filter.add_stream_handler(console_config)

# Add a negative keyword filter (hide logs with "DEBUG")
negative_filter.add_keyword_filter("DEBUG", positive=False)

negative_filter.logger.debug("This is a DEBUG message.")  # Will be filtered out
negative_filter.logger.info("Another INFO message.")  # Will be shown
