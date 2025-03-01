import sys
import logging
from tz_logging.core import TzLogger, StreamHandlerConfig

# Step 1: Initialize the logger
logger_instance = TzLogger("dynamic_logger")

# Step 2: Add a stream handler
console_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)
logger_instance.add_stream_handler(console_config)

# Step 3: Log messages normally
logger_instance.logger.debug("DEBUG - Not shown because level is INFO.")
logger_instance.logger.info("INFO - This should be displayed.")
logger_instance.logger.warning("WARNING - This should be displayed.")

# Step 4: Temporarily change log level to DEBUG
logger_instance.set_temporary_log_level(logging.DEBUG)

# Step 5: Log messages while at DEBUG level
logger_instance.logger.debug("DEBUG - Now visible because level was temporarily set to DEBUG.")
logger_instance.logger.info("INFO - Still visible.")
logger_instance.logger.warning("WARNING - Still visible.")

# Step 6: Restore original log level
logger_instance.restore_log_level()

# Step 7: Log messages again to verify restoration
logger_instance.logger.debug("DEBUG - Should NOT be visible again.")
logger_instance.logger.info("INFO - Should be displayed as before.")
logger_instance.logger.warning("WARNING - Should be displayed as before.")
