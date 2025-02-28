from tz_logging import TzLogger, RotatingFileHandlerConfig
import logging


file_config = RotatingFileHandlerConfig(
    file_path="custom_log.log",
    max_bytes=2 * 1024 * 1024,  # 2 MB
    backup_count=2,
    level=logging.INFO
)

# Initialize logger
logger = TzLogger("example_logger")
logger.add_rotating_file_handler(file_config)

# Log messages
logger.logger.debug("This is a debug message.")
logger.logger.info("This is an info message.")
logger.logger.warning("This is a warning message.")
logger.logger.error("This is an error message.")
