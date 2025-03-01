import sys
import logging
from tz_logging.core import TzLogger, StreamHandlerConfig

# Step 1: Initialize the logger with a blank configuration
logger_instance = TzLogger("format_demo_logger")

# Step 2: Set the logger level to DEBUG to capture all messages
logger_instance.logger.setLevel(logging.DEBUG)

# Step 3: Use built-in format strings for different handlers
# Each handler will use a different format to demonstrate their differences.

# 🟢 FORMAT_DETAILED: Includes file name, function, and line number
detailed_config = StreamHandlerConfig(stream=sys.stdout, level=logging.DEBUG, format_str=TzLogger.FORMAT_DETAILED)
logger_instance.add_stream_handler(detailed_config)

# 🟡 FORMAT_STANDARD: More concise but still includes location details
standard_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO, format_str=TzLogger.FORMAT_STANDARD)
logger_instance.add_stream_handler(standard_config)

# 🔵 FORMAT_SIMPLE: Minimal log format, just level, timestamp, and message
simple_config = StreamHandlerConfig(stream=sys.stdout, level=logging.WARNING, format_str=TzLogger.FORMAT_SIMPLE)
logger_instance.add_stream_handler(simple_config)

# 🔴 Custom Format: Adding a thread name and module name to the log format
CUSTOM_FORMAT = "[%(levelname)s] %(asctime)s [%(threadName)s] [%(module)s]: %(message)s"
custom_config = StreamHandlerConfig(stream=sys.stdout, level=logging.ERROR, format_str=CUSTOM_FORMAT)
logger_instance.add_stream_handler(custom_config)

# Step 4: Log messages at different levels to see how they appear in each format
logger_instance.logger.debug("DEBUG - This message appears only in detailed format.")
logger_instance.logger.info("INFO - This message appears in detailed and standard formats.")
logger_instance.logger.warning("WARNING - This message appears in detailed, standard, and simple formats.")
logger_instance.logger.error("ERROR - This message appears in all formats, including custom format.")
logger_instance.logger.critical("CRITICAL - This message appears in all formats.")

print("Logging demonstration complete. Observe the different log formats in the console.")

# More available LogRecord attributes can be found at:
# https://docs.python.org/3/library/logging.html#logrecord-objects
