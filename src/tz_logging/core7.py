import logging
import re
import json
import yaml
import os
import time
import threading

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

class LogHandler:
    """
    Standalone handler-based logging system.
    Developers only interact with handlers, not loggers.
    """

    _global_logger = logging.getLogger("handler_logger")
    _handler_registry = {}
    _config_file = None
    _stop_event = threading.Event()
    
    def __init__(self, name, level=logging.INFO, fmt="%(asctime)s - %(levelname)s - %(message)s", output="console", include_filter=None, exclude_filter=None, file_filter=None, level_filter=None):
        """
        Create a named log handler.
        """
        self.name = name
        self.level = level
        self.include_filter = include_filter
        self.exclude_filter = exclude_filter
        self.file_filter = file_filter  # New: Filter by file name
        self.level_filter = level_filter  # New: Filter by log level

        # Create handler
        if output == "console":
            self.handler = logging.StreamHandler()
        else:
            self.handler = logging.FileHandler(output)

        self.handler.setLevel(level)
        self.formatter = logging.Formatter(fmt)
        self.handler.setFormatter(self.formatter)
        self.handler.addFilter(self)

        # Attach handler to logger
        self._global_logger.addHandler(self.handler)
        
        # Register handler
        LogHandler._handler_registry[name] = self
        LogHandler._update_global_log_level()
        
    def filter(self, record):
        """Filters log messages based on include/exclude patterns, file name, and log level."""
        message = record.getMessage()
        
        if self.include_filter and not re.search(self.include_filter, message):
            return False
        if self.exclude_filter and re.search(self.exclude_filter, message):
            return False
        if self.file_filter and not re.search(self.file_filter, record.pathname):
            return False
        if self.level_filter and record.levelno != self.level_filter:
            return False
        return True

    @staticmethod
    def log(level, message):
        """Log a message through the logger."""
        LogHandler._global_logger.log(level, message)

    def set_level(self, level):
        """Change the logging level of this handler."""
        self.level = level
        self.handler.setLevel(level)
        LogHandler._update_global_log_level()
    
    def set_formatter(self, fmt):
        """Set a new formatter for this handler."""
        self.formatter = logging.Formatter(fmt)
        self.handler.setFormatter(self.formatter)
        print(f"[LOG HANDLER] Formatter updated for: {self.name}")
    
    def reset_formatter(self):
        """Reset the handler's formatter to default."""
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.handler.setFormatter(self.formatter)
        print(f"[LOG HANDLER] Formatter reset for: {self.name}")
    
    @classmethod
    def list_handlers(cls):
        """List all registered handlers."""
        return list(cls._handler_registry.keys())
    
    @classmethod
    def remove_handler(cls, name):
        """Remove a handler by name."""
        if name in cls._handler_registry:
            handler = cls._handler_registry.pop(name)
            cls._global_logger.removeHandler(handler.handler)
            print(f"[LOG HANDLER] Removed handler: {name}")
            cls._update_global_log_level()
        else:
            print(f"[LOG HANDLER] Handler not found: {name}")
    
    @classmethod
    def modify_handler(cls, name, level=None, include_filter=None, exclude_filter=None, file_filter=None, level_filter=None, formatter=None):
        """Modify an existing handler's settings."""
        if name in cls._handler_registry:
            handler = cls._handler_registry[name]
            if level:
                handler.set_level(level)
            if include_filter is not None:
                handler.include_filter = include_filter
            if exclude_filter is not None:
                handler.exclude_filter = exclude_filter
            if file_filter is not None:
                handler.file_filter = file_filter
            if level_filter is not None:
                handler.level_filter = level_filter
            if formatter is not None:
                handler.set_formatter(formatter)
            print(f"[LOG HANDLER] Modified handler: {name}")
        else:
            print(f"[LOG HANDLER] Handler not found: {name}")

    @classmethod
    def _update_global_log_level(cls):
        """Ensures the logger level matches the strictest handler level."""
        if cls._handler_registry:
            min_level = min(handler.level for handler in cls._handler_registry.values())
            cls._global_logger.setLevel(min_level)

    @classmethod
    def load_from_config(cls, config_file):
        """Load log handlers from a configuration file (JSON or YAML)."""
        cls._config_file = os.path.abspath(config_file)
        
        with open(cls._config_file, "r") as f:
            if config_file.endswith(".json"):
                config = json.load(f)
            elif config_file.endswith(".yaml") or config_file.endswith(".yml"):
                config = yaml.safe_load(f)
            else:
                raise ValueError("Unsupported configuration format. Use JSON or YAML.")
        
        # Remove existing handlers
        for handler in list(cls._handler_registry.values()):
            cls._global_logger.removeHandler(handler.handler)
        cls._handler_registry.clear()
        
        for handler_config in config.get("handlers", []):
            LogHandler(
                name=handler_config["name"],
                level=getattr(logging, handler_config.get("level", "INFO").upper()),
                fmt=handler_config.get("format", "%(asctime)s - %(levelname)s - %(message)s"),
                output=handler_config.get("output", "console"),
                include_filter=handler_config.get("include_filter"),
                exclude_filter=handler_config.get("exclude_filter"),
                file_filter=handler_config.get("file_filter"),
                level_filter=getattr(logging, handler_config.get("level_filter", "NOTSET").upper()) if handler_config.get("level_filter") else None
            )
        
        cls.start_config_watcher()
        LogHandler._update_global_log_level()
    
    @classmethod
    def start_config_watcher(cls):
        """Start watching the config file for changes."""
        if WATCHDOG_AVAILABLE:
            class ConfigHandler(FileSystemEventHandler):
                def on_modified(self, event):
                    if os.path.abspath(event.src_path) == cls._config_file:
                        print("[LOG HANDLER] Configuration changed. Reloading...")
                        cls.load_from_config(cls._config_file)

            observer = Observer()
            observer.schedule(ConfigHandler(), path=os.path.dirname(cls._config_file), recursive=False)
            observer.start()
        else:
            def poll_config():
                last_modified = os.path.getmtime(cls._config_file)
                while not cls._stop_event.is_set():
                    time.sleep(5)
                    if os.path.getmtime(cls._config_file) > last_modified:
                        last_modified = os.path.getmtime(cls._config_file)
                        print("[LOG HANDLER] Configuration changed. Reloading...")
                        cls.load_from_config(cls._config_file)
            
            threading.Thread(target=poll_config, daemon=True).start()
        print(f"[LOG HANDLER] Watching {cls._config_file} for changes... (Watchdog: {WATCHDOG_AVAILABLE})")
