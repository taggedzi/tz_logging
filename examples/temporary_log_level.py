import sys
import logging
from tz_logging.core import LogHandler

# Step 1: Initialize the logger
logger_instance = LogHandler("dynamic_logger")

# Step 3: Log messages normally
logging.debug("DEBUG - Not shown because level is INFO.")
logging.info("INFO - This should be displayed.")
logging.warning("WARNING - This should be displayed.")

# Step 4: Temporarily change log level to DEBUG
logger_instance.set_temporary_log_level(logging.DEBUG)

# Step 5: Log messages while at DEBUG level
logging.debug("DEBUG - Now visible because level was temporarily set to DEBUG.")
logging.info("INFO - Still visible.")
logging.warning("WARNING - Still visible.")

# Step 6: Restore original log level
logger_instance.restore_log_level()

# Step 7: Log messages again to verify restoration
logging.debug("DEBUG - Should NOT be visible again.")
logging.info("INFO - Should be displayed as before.")
logging.warning("WARNING - Should be displayed as before.")
