"""
Module providing the ability to quickly set up and configure logging.
"""

import logging
import logging.config
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
import yaml
from .config import RotatingFileHandlerConfig, StreamHandlerConfig


class TzLogger:
    """
    A configurable logger class that supports YAML-based configuration,
    temporary log level adjustments, and adding various handlers dynamically.
    """

    FORMAT_DETAILED = (
        "------------------------------------\n"
        "   Logging Level: %(levelname)s\n"
        " - Time:          %(asctime)s\n"
        " - File:          %(pathname)s\n"
        " - Function:      %(funcName)s\n"
        " - Line Number:   %(lineno)d\n"
        " - Message:       %(message)s\n"
        "------------------------------------"
    )

    FORMAT_STANDARD = (
        "[%(levelname)s] %(asctime)s\n"
        "[%(pathname)s] %(funcName)s Line: %(lineno)d\n"
        "%(message)s"
    )

    FORMAT_SIMPLE = "[%(levelname)s] %(asctime)s:  %(message)s"

    def __init__(self, name: str = "tz_logger"):
        """
        Initializes the logger with a blank (minimal) configuration.
        No YAML or external configuration is loaded automatically.

        Args:
            name (str): The name of the logger.
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Allow all logs to be processed
        self._original_levels = {}  # Store original levels for restoration

    def set_temporary_log_level(self, level: int) -> None:
        """
        Temporarily changes the log level for all handlers attached to the logger.

        Args:
            level (int): The new log level (e.g., logging.DEBUG, logging.INFO, etc.).
        """
        self._original_levels = {handler: handler.level for handler in self.logger.handlers}

        for handler in self.logger.handlers:
            handler.setLevel(level)

        print(f"Log level temporarily set to {logging.getLevelName(level)}")

    def restore_log_level(self) -> None:
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
        Loads a YAML configuration file to configure the logger.

        Args:
            config_file (Optional[str]): Path to the YAML configuration file.
                                         If None, the environment variable TZ_LOGGING_CONFIG_FILE is used.

        Raises:
            FileNotFoundError: If no configuration file is found.
        """
        config_file = config_file or os.getenv("TZ_LOGGING_CONFIG_FILE")

        if not config_file or not os.path.exists(config_file):
            raise FileNotFoundError(
                "No YAML configuration file specified or found. "
                "Set TZ_LOGGING_CONFIG_FILE or pass a file path explicitly."
            )

        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        logging.config.dictConfig(config)
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.getLogger().level)  # Sync with root logger

    def add_stream_handler(self, config: StreamHandlerConfig) -> logging.Handler:
        """
        Adds a stream handler to the logger using the provided configuration.

        Args:
            config (StreamHandlerConfig): Configuration object for the stream handler.

        Returns:
            logging.Handler: The created StreamHandler instance.

        Raises:
            ValueError: If the config parameter is None.
        """
        if not config:
            raise ValueError("StreamHandlerConfig is required")

        handler = logging.StreamHandler(config.stream)
        handler.setLevel(config.level)
        formatter = logging.Formatter(config.format_str or self.FORMAT_SIMPLE)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        return handler

    def add_rotating_file_handler(self, config: RotatingFileHandlerConfig) -> None:
        """
        Adds a rotating file handler to the logger using the provided configuration.

        Args:
            config (RotatingFileHandlerConfig): Configuration object for the file handler.

        Raises:
            FileNotFoundError: If the log directory does not exist.
            PermissionError: If the log directory is not writable.
        """
        log_dir = os.path.dirname(config.file_path)

        if not os.path.exists(log_dir):
            raise FileNotFoundError(f"Log directory does not exist: {log_dir}")

        if not os.access(log_dir, os.W_OK):
            raise PermissionError(f"Cannot write to log directory: {log_dir}")

        handler = RotatingFileHandler(
            config.file_path, maxBytes=config.max_bytes, backupCount=config.backup_count
        )
        handler.setLevel(config.level)
        formatter = logging.Formatter(config.format_str or self.FORMAT_STANDARD)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def add_filter(self, log_filter: logging.Filter) -> None:
        """
        Adds a custom filter to all existing handlers.

        Args:
            log_filter (logging.Filter): The filter instance to apply to all handlers.
        """
        for handler in self.logger.handlers:
            handler.addFilter(log_filter)
