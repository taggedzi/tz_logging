import logging
from tz_logging.core import LogHandler

# Step 1: Initialize the LogHandler with the name "file_logger" and log to "logs/app.log"
LogHandler("file_logger", output="logs/app.log")

# Step 4: Log some messages to verify that logs are written to the file
logging.debug("This is a DEBUG message (won't be logged since level is INFO).")
logging.info("This is an INFO message (should be logged).")
logging.warning("This is a WARNING message (should be logged).")
logging.error("This is an ERROR message (should be logged).")
logging.critical("This is a CRITICAL message (should be logged).")

print("Logs are being written to logs/app.log")
