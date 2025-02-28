"""A sample file to demonstrate how to use custom format types. """
from tz_logging import TzLogger, StreamHandlerConfig

# More available LogRecord attributes can be found at:
# https://docs.python.org/3/library/logging.html#logrecord-objects
CUSTOM_FORMAT = '\n'.join([
    '*** [%(levelname)s] %(asctime)s ',
    '%(message)s'
])

print('---------------- Custom Log Format')
# Initialize logger
custom_log = TzLogger("custom_log")

# Add a stream handler with simple formatting
stream_config = StreamHandlerConfig(format_str=CUSTOM_FORMAT)
custom_log.add_stream_handler(stream_config)

# Log messages
custom_log.logger.debug("This is a custom debug message format.")
custom_log.logger.info("This is a custom info message format.")
custom_log.logger.warning("This is a custom warning message format.")
custom_log.logger.error("This is a custom error message format.")
