import logging
from tz_logging.core import LogHandler

# Step 1: Initialize the logger with a blank configuration
LogHandler("simple_logger")

# Step 2: Log some sample messages to verify it works
logging.debug("This is a DEBUG message (will not be displayed since level is INFO).")
logging.info("This is an INFO message (should be displayed).")
logging.warning("This is a WARNING message (should be displayed).")
logging.error("This is an ERROR message (should be displayed).")
logging.critical("This is a CRITICAL message (should be displayed).")
