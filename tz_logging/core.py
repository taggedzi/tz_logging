"""
Module providing the ability to quickly setup and configure logging.
"""
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict
from .config import RotatingFileHandlerConfig, StreamHandlerConfig


class TzLogger:

    FORMAT_DETAILED = '\n'.join([
        '------------------------------------',
        '   Logging Level: %(levelname)s',
        ' - Time:          %(asctime)s',
        ' - File:          %(pathname)s',
        ' - Function:      %(funcName)s',
        ' - Line Number:   %(lineno)d',
        ' - Message:       %(message)s',
        '------------------------------------'
    ])
    FORMAT_STANDARD = '\n'.join([
        '[%(levelname)s] %(asctime)s',
        '[%(pathname)s] %(funcName)s Line: %(lineno)d',
        '%(message)s'
    ])
    FORMAT_SIMPLE = '\n'.join([
        '[%(levelname)s] %(asctime)s:  %(message)s'
    ])

    def __init__(self, name: str = 'tz_logger', config: Optional[Dict] = None):
        """
        Initializes the logger. If a configuration dictionary is provided,
        it uses dictConfig to set up the logger.

        Args: 
            name (str): The name of the logger
            config (Optional[Dict]): a dictionary describing the configuration of the logger.
        """
        self.name = name
        self.logger = logging.getLogger(name)
        if config:
            self.configure_logger(config)
        else:
            self.logger.setLevel(logging.DEBUG)

    def configure_logger(self, config: Dict):
        """
        Configures the logger using a configuration dictionary.
        This method leverages logging.config.dictConfig for maximum flexibility.

        Args: 
            config (Optional[Dict]): a dictionary describing the configuration of the logger.
        """
        logging.config.dictConfig(config)
        # Refresh the logger after applying the configuration
        self.logger = logging.getLogger(self.name)

    def add_stream_handler(self, config: StreamHandlerConfig):
        """
        Adds a stream handler to the logger using the provided configuration.

        Args: 
            config (Optional[Dict]): a dictionary describing the configuration of the logger.
        """
        handler = logging.StreamHandler(config.stream)
        handler.setLevel(config.level)
        formatter = logging.Formatter(config.format_str or self.FORMAT_STANDARD)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def add_rotating_file_handler(self, config: RotatingFileHandlerConfig):
        """
        Adds a rotating file handler to the logger using the provided configuration.
        """
        handler = RotatingFileHandler(
            config.file_path,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count
        )
        handler.setLevel(config.level)
        format_str = config.format_str or self.FORMAT_STANDARD
        formatter = logging.Formatter(format_str)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def add_filter(self, log_filter: logging.Filter):
        """
        Adds a custom filter to all existing handlers.
        """
        for handler in self.logger.handlers:
            handler.addFilter(log_filter)


if __name__ == "__main__":
    pass
