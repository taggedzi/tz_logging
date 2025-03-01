import logging
from tz_logging.core import TzLogger, RotatingFileHandlerConfig

# Step 1: Initialize the logger with a blank configuration
logger_instance = TzLogger("file_logger")

# Step 2: Configure a rotating file handler
# - Logs will be written to "logs/app.log"
# - Max file size is 1MB (1 * 1024 * 1024 bytes)
# - Keeps up to 3 backup files before overwriting old logs
file_config = RotatingFileHandlerConfig(
    file_path="logs/app.log",
    max_bytes=1 * 1024 * 1024,
    backup_count=3,
    level=logging.INFO
)

# Step 3: Add the file handler to the logger
logger_instance.add_rotating_file_handler(file_config)

# Step 4: Log some messages to verify that logs are written to the file
logger_instance.logger.debug("This is a DEBUG message (won't be logged since level is INFO).")
logger_instance.logger.info("This is an INFO message (should be logged).")
logger_instance.logger.warning("This is a WARNING message (should be logged).")
logger_instance.logger.error("This is an ERROR message (should be logged).")
logger_instance.logger.critical("This is a CRITICAL message (should be logged).")

print("Logs are being written to logs/app.log")
