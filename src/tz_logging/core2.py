import logging
import re
import json
import yaml

class LogHandler:
    """
    Standalone handler-based logging system.
    Developers only interact with handlers, not loggers.
    """

    _global_logger = logging.getLogger()  # Use root logger
    _global_logger.setLevel(logging.DEBUG)  # Default lowest level
    _handler_registry = {}  # Track named handlers

    def __init__(self, name, level=logging.INFO, fmt="%(asctime)s - %(levelname)s - %(message)s", output="console", include_filter=None, exclude_filter=None):
        """
        Create a named log handler.
        
        :param name: Unique handler name
        :param level: Logging level (INFO, DEBUG, etc.)
        :param fmt: Log message format
        :param output: "console" for stdout, or a filename for file logging
        :param include_filter: Regex pattern to include only matching messages
        :param exclude_filter: Regex pattern to exclude matching messages
        """
        self.name = name
        self.level = level
        self.include_filter = include_filter
        self.exclude_filter = exclude_filter

        # Create handler
        if output == "console":
            self.handler = logging.StreamHandler()
        else:
            self.handler = logging.FileHandler(output)

        self.handler.setLevel(level)
        self.formatter = logging.Formatter(fmt)
        self.handler.setFormatter(self.formatter)
        self.handler.addFilter(self)

        # Attach handler to global logger
        self._global_logger.addHandler(self.handler)
        
        # Register handler
        LogHandler._handler_registry[name] = self

    def filter(self, record):
        """Filters log messages based on include/exclude patterns."""
        message = record.getMessage()
        
        if self.include_filter and not re.search(self.include_filter, message):
            return False  # Exclude if it doesn't match positive filter
        if self.exclude_filter and re.search(self.exclude_filter, message):
            return False  # Exclude if it matches negative filter
        
        return True

    def set_filter(self, include_pattern=None, exclude_pattern=None):
        """Set positive and/or negative filtering using regex patterns."""
        self.include_filter = include_pattern
        self.exclude_filter = exclude_pattern

    @staticmethod
    def log(level, message):
        """Log a message through the root logger."""
        LogHandler._global_logger.log(level, message)

    def set_level(self, level):
        """Change the logging level of this handler."""
        self.level = level
        self.handler.setLevel(level)

    @classmethod
    def get_handler(cls, name):
        """Retrieve a handler by name."""
        return cls._handler_registry.get(name)

    @classmethod
    def list_handlers(cls):
        """List all registered handlers."""
        return list(cls._handler_registry.keys())

    def remove(self):
        """Remove this handler from the system."""
        LogHandler._global_logger.removeHandler(self.handler)
        del LogHandler._handler_registry[self.name]
    
    @classmethod
    def load_from_config(cls, config_file):
        """Load log handlers from a configuration file (JSON or YAML)."""
        with open(config_file, "r") as f:
            if config_file.endswith(".json"):
                config = json.load(f)
            elif config_file.endswith(".yaml") or config_file.endswith(".yml"):
                config = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported configuration format. Use JSON or YAML.")
        
        for handler_config in config.get("handlers", []):
            LogHandler(
                name=handler_config["name"],
                level=getattr(logging, handler_config.get("level", "INFO").upper()),
                fmt=handler_config.get("format", "%(asctime)s - %(levelname)s - %(message)s"),
                output=handler_config.get("output", "console"),
                include_filter=handler_config.get("include_filter"),
                exclude_filter=handler_config.get("exclude_filter")
            )

# ===================
# 🚀 Hijack logging.* calls
# ===================
logging.debug = lambda msg: LogHandler.log(logging.DEBUG, msg)
logging.info = lambda msg: LogHandler.log(logging.INFO, msg)
logging.warning = lambda msg: LogHandler.log(logging.WARNING, msg)
logging.error = lambda msg: LogHandler.log(logging.ERROR, msg)
logging.critical = lambda msg: LogHandler.log(logging.CRITICAL, msg)

# ===================
# 🚀 Example Usage:
# ===================
if __name__ == "__main__":
    console_log = LogHandler("console", logging.DEBUG)
    file_log = LogHandler("file_output", logging.WARNING, output="app.log")

    # Apply filtering: Only allow messages containing "error", exclude messages with "debug"
    file_log.set_filter(include_pattern="error", exclude_pattern="debug")

    # Load configuration from file (JSON or YAML)
    # LogHandler.load_from_config("log_config.json")
    # LogHandler.load_from_config("log_config.yaml")
    
    logging.debug("This is a debug message.")   # Console only (filtered from file)
    logging.info("This is an info message.")    # Console only
    logging.warning("This is a warning.")       # Console + File
    logging.error("This is an error message!") # Console + File (matches include filter)
    
    print("Active Handlers:", LogHandler.list_handlers())
    console_log.remove()
