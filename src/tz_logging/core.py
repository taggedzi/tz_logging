import logging
import re
import json
import os
import queue
import time
import threading
from queue import Queue
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, SysLogHandler
import requests
import yaml

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

class JSONFormatter(logging.Formatter):
    """JSON formatter

    Args:
        logging (logging.Formatter): a logging formatter.
    """
    def __init__(self, extra_fields=None):
        super().__init__()
        self.extra_fields = extra_fields or {}

    # Custom formatter to output logs in JSON format.
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "file": record.pathname,
            "line": record.lineno,
            **self.extra_fields
        }
        return json.dumps(log_record)

class AsyncRemoteHandler(logging.Handler):
    """Custom handler to send logs asynchronously to a remote HTTP endpoint."""
    def __init__(self, url, method="POST", max_queue_size=1000):
        super().__init__()
        self.url = url
        self.method = method
        self.log_queue = Queue(maxsize=max_queue_size)
        self._start_worker()

    def emit(self, record):
        log_entry = self.format(record)
        try:
            try:
                self.log_queue.put_nowait(log_entry)
            except queue.Full:
                print("[LOG HANDLER] Queue full. Dropping log:", log_entry)
        except queue.Full:
            print("[LOG HANDLER] Dropped log due to full queue")

    def _send_log(self, log_entry):
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.request(self.method, self.url, json={"log": log_entry}, timeout=300)
                if response.status_code == 200:
                    return
            except requests.RequestException as e:
                print(f"[LOG HANDLER] Failed to send log (attempt {attempt+1}/{retries}): {e}")
                time.sleep(2 ** attempt)

    def _start_worker(self):
        def worker():
            while True:
                log_entry = self.log_queue.get()
                self._send_log(log_entry)
                self.log_queue.task_done()
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

class LogHandler:
    """
    Standalone handler-based logging system.
    Developers only interact with handlers, not loggers.
    """

    _global_logger = logging.getLogger("handler_logger")
    _handler_registry = {}
    _config_file = None
    _stop_event = threading.Event()
    
    def __init__(self,
                 name,
                 level=logging.INFO,
                 fmt="%(asctime)s - %(levelname)s - %(message)s",
                 output="console",
                 include_filter=None,
                 exclude_filter=None,
                 file_filter=None,
                 level_filter=None,
                 rolling_type=None,
                 rolling_value=None,
                 backup_count=5,
                 json_format=False,
                 extra_fields=None,
                 remote_url=None,
                 syslog_address=None):

        """
        Create a named log handler.
        """
        self.name = name
        self.level = level
        self.include_filter = include_filter
        self.exclude_filter = exclude_filter
        self.file_filter = file_filter
        self.level_filter = level_filter

        # Create handler
        if remote_url:
            print(f"[DEBUG] Creating AsyncRemoteHandler for {remote_url}")  # Debugging line
            self.handler = AsyncRemoteHandler(remote_url)
        elif output == "console":
            self.handler = logging.StreamHandler()
        elif syslog_address:
            self.handler = SysLogHandler(address=syslog_address)
        elif rolling_type == "size":
            self.handler = RotatingFileHandler(output, maxBytes=rolling_value, backupCount=backup_count)
        elif rolling_type == "time":
            self.handler = TimedRotatingFileHandler(output, when=rolling_value, interval=1, backupCount=backup_count)
        else:
            self.handler = logging.FileHandler(output)

        self.handler.setLevel(level)
        self.formatter = JSONFormatter(extra_fields) if json_format else logging.Formatter(fmt)
        self.handler.setFormatter(self.formatter)
        self.handler.addFilter(self)

        # Attach handler to logger
        self._global_logger.addHandler(self.handler)
        
        # Register handler
        LogHandler._handler_registry[name] = self
        LogHandler._update_global_log_level()
        logging.debug("[LOG HANDLER] Created handler '%s' with level %s", name, str(level))
        
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
        logging.debug("[LOG HANDLER] Loading config from %s", config_file)
        
        try:
            with open(cls._config_file, "r", encoding="utf-8") as f:
                if config_file.endswith(".json"):
                    config = json.load(f)
                else:
                    config = yaml.safe_load(f)
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Error loading config file: {e}") from e
        
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
                level_filter=getattr(logging, handler_config.get("level_filter", "NOTSET").upper()) if handler_config.get("level_filter") else None,
                rolling_type=handler_config.get("rolling_type"),
                rolling_value=handler_config.get("rolling_value"),
                backup_count=handler_config.get("backup_count", 5),
                json_format=handler_config.get("json_format", False),
                extra_fields=handler_config.get("extra_fields"),
                remote_url=handler_config.get("remote_url"),
                syslog_address=handler_config.get("syslog_address")
            )
        
        cls._update_global_log_level()
    
    @classmethod
    def start_config_watcher(cls):
        """Start watching the config file for changes."""
        if WATCHDOG_AVAILABLE:
            class ConfigHandler(FileSystemEventHandler):
                """Class to setup and handle watchdog events."""
                def on_modified(self, event):
                    if os.path.abspath(event.src_path) == cls._config_file:
                        print("[LOG HANDLER] Configuration changed. Reloading...")
                        cls.load_from_config(cls._config_file)

            observer = Observer()
            observer.schedule(ConfigHandler(), path=os.path.dirname(cls._config_file), recursive=False)
            observer.start()
        print(f"[LOG HANDLER] Watching {cls._config_file} for changes... (Watchdog: {WATCHDOG_AVAILABLE})")


#### Simple example
# # Create a console handler with ERROR level and detailed format
# error_console_handler = LogHandler(
#     name="console_error",
#     level=logging.ERROR,
#     fmt="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
#     output="console"
# )
# # Generate test logs
# logging.debug("This is a DEBUG message.")  # Will not show
# logging.info("This is an INFO message.")  # Will not show
# logging.warning("This is a WARNING message.")  # Will not show
# logging.error("This is an ERROR message.")  # Will be displayed
# logging.critical("This is a CRITICAL message.")  # Will be displayed


# console_json_handler = LogHandler("console_json", output="console", json_format=True)
# console_json_handler = LogHandler("console_json", output="console", json_format=True, extra_fields={"app": "my_app"})
# remote_log_handler = LogHandler("remote_logger", remote_url="https://localhost/logs")

# logging.info("Test structured log message.")