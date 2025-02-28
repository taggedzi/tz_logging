from tz_logging.core import TzLogger, StreamHandlerConfig

logger = TzLogger("my_log")
logger.add_stream_handler(StreamHandlerConfig())

logger.logger.info("Info Test run")
logger.logger.debug("Debug Test run")
logger.logger.warning("Warning Test run")
logger.logger.error("Error Test run")
