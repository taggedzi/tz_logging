"""
Module providing the ability to quickly setup and configure logging.
"""
import logging
import logging.config
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
import yaml
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

    def __init__(self, name: str = 'tz_logger'):
        """
        Initializes the logger with a blank (minimal) configuration.
        No YAML or external configuration is loaded automatically.
        The developer can later call load_yaml_config() to load a YAML file,
        or add handlers and filters manually.
        
        Args:
            name (str): The name of the logger.
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Allow all logs to be processed
        self._original_levels = {}  # Store original levels for restoration

    def set_temporary_log_level(self, level: int):
        """
        Temporarily changes the log level for all handlers attached to the logger.

        Args:
            level (int): The new log level (e.g., logging.DEBUG, logging.INFO, etc.).
        """
        self._original_levels = {handler: handler.level for handler in self.logger.handlers}

        for handler in self.logger.handlers:
            handler.setLevel(level)

        print(f"Log level temporarily set to {logging.getLevelName(level)}")

    def restore_log_level(self):
        """
        Restores the original log level for all handlers after a temporary change.
        """
        if self._original_levels:
            for handler, original_level in self._original_levels.items():
                handler.setLevel(original_level)

            print("Log levels restored to their original values.")
        else:
            print("No previous log level stored. Nothing to restore.")

        self._original_levels.clear()  # Clear stored levels after restoration


    def load_yaml_config(self, config_file: Optional[str] = None) -> None:
        """
        Explicitly loads a YAML configuration file to configure the logger.
        If no config_file is provided, this method will check for the environment
        variable 'TZ_LOGGING_CONFIG_FILE'. If that is also not set, an exception is raised.
        
        After loading the configuration via logging.config.dictConfig(), the logger is refreshed.
        
        Args:
            config_file (Optional[str]): The path to the YAML configuration file.
                                         If None, the environment variable TZ_LOGGING_CONFIG_FILE
                                         is used.
        
        Raises:
            FileNotFoundError: If no configuration file is found.
        """
        # Determine the configuration file to use.
        if not config_file:
            config_file = os.getenv("TZ_LOGGING_CONFIG_FILE")

        if not config_file or not os.path.exists(config_file):
            raise FileNotFoundError("No YAML configuration file specified or found. "
                                    "Set TZ_LOGGING_CONFIG_FILE or pass a file path explicitly.")
        # Load YAML configuration
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        logging.config.dictConfig(config)

        # Ensure the logger updates to match the configuration's root level
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.getLogger().level)  # Sync with root logger

    def add_stream_handler(self, config: StreamHandlerConfig):
        """
        Adds a stream handler to the logger using the provided configuration.

        Args: 
            config (Optional[Dict]): a dictionary describing the configuration of the logger.
        """
        if config is None:
            raise ValueError("StreamHandlerConfig is required")
        
        handler = logging.StreamHandler(config.stream)
        handler.setLevel(config.level)
        formatter = logging.Formatter(config.format_str or self.FORMAT_SIMPLE)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        return handler

    def add_rotating_file_handler(self, config: RotatingFileHandlerConfig):
        """
        Adds a rotating file handler to the logger using the provided configuration.
        """
        log_dir = os.path.dirname(config.file_path)

        # Check if the directory exists and is writable
        if not os.path.exists(log_dir):
            raise FileNotFoundError(f"Log directory does not exist: {log_dir}")

        if not os.access(log_dir, os.W_OK):
            raise PermissionError(f"Cannot write to log directory: {log_dir}")
        
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

