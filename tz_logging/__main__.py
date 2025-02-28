import sys
import logging
from tz_logging.core import TzLogger
from tz_logging.config import StreamHandlerConfig

def main():
    """Main function to demonstrate a simple model of how this could be used.
    """
    print("\n".join([
        "tz_logging: This is a small library intended to implement easier ",
        "setup and config of logging in python applications."
        ]))

    logger = TzLogger("tz_logging")
    stream_config = StreamHandlerConfig(stream=sys.stdout, level=logging.DEBUG)
    logger.add_stream_handler(stream_config)

    logger.logger.info("tz_logging initialized with level: logging.DEBUG")
    logger.logger.debug("This is a debug message.")
    logger.logger.warning("This is a warning message.")
    logger.logger.error("This is an error message.")

if __name__ == "__main__":
    main()
