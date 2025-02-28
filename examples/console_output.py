from tz_logging import TzLogger, StreamHandlerConfig
import logging


# Initialize logger
logger = TzLogger("example_logger")

# Add a stream handler with default settings
stream_config = StreamHandlerConfig(level=logging.DEBUG)
logger.add_stream_handler(stream_config)

# Log messages
logger.logger.debug("This is a debug message.")
logger.logger.info("This is an info message.")
logger.logger.warning("This is a warning message.")
logger.logger.error("This is an error message.")
