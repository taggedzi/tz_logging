import os
from tz_logging.core import TzLogger

# Step 1: Set the environment variable to point to the YAML configuration file
os.environ["TZ_LOGGING_CONFIG_FILE"] = "config/sample_logging_1.yaml"

# Step 2: Initialize the logger
logger_instance = TzLogger("env_logger")

# Step 3: Load the YAML configuration from the environment variable
logger_instance.load_yaml_config()

# Step 4: Log messages at different levels
logger_instance.logger.debug("DEBUG - Should be logged if the YAML allows it.")
logger_instance.logger.info("INFO - This message should appear based on YAML settings.")
logger_instance.logger.warning("WARNING - This is a warning message.")
logger_instance.logger.error("ERROR - This is an error message.")
logger_instance.logger.critical("CRITICAL - This is a critical error.")

print("Logging has been configured via the environment variable!")

# Step 5: Unset the environment variable 
# THIS IS ONLY FOR THE EXAPLE SCRIPT SO THE CONFIG DOES NOT RESIDE 
# BEYOND IT'S EXECUTION.
os.environ.pop("TZ_LOGGING_CONFIG_FILE", None)

print("Environment variable has been unset!")
