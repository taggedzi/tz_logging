"""A sample file to demonstrate how to use the built in TzLogger format types. """
import logging     # This is only used to access logging level constants.
from tz_logging import TzLogger, StreamHandlerConfig


print('---------------- Simple Log Format')
# Initialize logger
simple_log = TzLogger("simple_log")

# Add a stream handler with simple formatting
stream_config = StreamHandlerConfig(level=logging.DEBUG, format_str=TzLogger.FORMAT_SIMPLE)
simple_log.add_stream_handler(stream_config)

# Log messages
simple_log.logger.debug("This is a simple debug message format.")
simple_log.logger.info("This is a simple info message format.")
simple_log.logger.warning("This is a simple warning message format.")
simple_log.logger.error("This is a simple error message format.")


print('---------------- Standard Log Format')
# Initialize logger
standard_log = TzLogger("standard_log")

# Add a stream handler with standard formatting
stream_config = StreamHandlerConfig(level=logging.DEBUG, format_str=TzLogger.FORMAT_STANDARD)
standard_log.add_stream_handler(stream_config)

# Log messages
standard_log.logger.debug("This is a standard debug message format.")
standard_log.logger.info("This is a standard info message format.")
standard_log.logger.warning("This is a standard warning message format.")
standard_log.logger.error("This is a standard error message format.")


print('---------------- Detailed Log Format')
# Initialize logger
detailed_log = TzLogger("detailed_log")

# Add a stream handler with detailed formatting
stream_config = StreamHandlerConfig(level=logging.DEBUG, format_str=TzLogger.FORMAT_DETAILED)
detailed_log.add_stream_handler(stream_config)

# Log messages
detailed_log.logger.debug("This is a detailed debug message format.")
detailed_log.logger.info("This is a detailed info message format.")
detailed_log.logger.warning("This is a detailed warning message format.")
detailed_log.logger.error("This is a detailed error message format.")
