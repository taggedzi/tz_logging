import sys
import logging
from tz_logging.core import TzLogger, StreamHandlerConfig

# Step 1: Initialize the logger
logger_instance = TzLogger("filter_demo_logger")
logger_instance.logger.setLevel(logging.DEBUG)  # Ensure all levels are allowed

# Step 2: Define custom filters

class ErrorTypeFilter(logging.Filter):
    """Allows only log messages related to a specific error type (ValueError)."""
    def filter(self, record):
        return "ValueError" in record.getMessage()  # Only logs mentioning ValueError will pass

class KeywordFilter(logging.Filter):
    """Allows only log messages containing a specific keyword."""
    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword

    def filter(self, record):
        return self.keyword in record.getMessage()

class FileFilter(logging.Filter):
    """Filters log messages coming from a specific file (log_filter_demo.py)."""
    def filter(self, record):
        return "log_filter_demo.py" in record.pathname  # Only logs from this file pass

# Step 3: Create handlers with filters

# 🟢 Handler 1: Only logs messages containing "ValueError"
error_filter_handler = StreamHandlerConfig(stream=sys.stdout, level=logging.DEBUG, format_str=TzLogger.FORMAT_STANDARD)
logger_instance.add_stream_handler(error_filter_handler)
logger_instance.logger.handlers[-1].addFilter(ErrorTypeFilter())

# 🟡 Handler 2: Only logs messages containing "critical_issue"
keyword_filter_handler = StreamHandlerConfig(stream=sys.stdout, level=logging.DEBUG, format_str=TzLogger.FORMAT_STANDARD)
logger_instance.add_stream_handler(keyword_filter_handler)
logger_instance.logger.handlers[-1].addFilter(KeywordFilter("critical_issue"))

# 🔵 Handler 3: Only logs messages coming from this script (log_filter_demo.py)
file_filter_handler = StreamHandlerConfig(stream=sys.stdout, level=logging.DEBUG, format_str=TzLogger.FORMAT_STANDARD)
logger_instance.add_stream_handler(file_filter_handler)
logger_instance.logger.handlers[-1].addFilter(FileFilter())

# Step 4: Log test messages

logger_instance.logger.debug("DEBUG - This is a normal debug message.")
logger_instance.logger.info("INFO - This contains a ValueError message!")  # Should appear in ErrorTypeFilter
logger_instance.logger.warning("WARNING - critical_issue detected in the system!")  # Should appear in KeywordFilter
logger_instance.logger.error("ERROR - Something went wrong in log_filter_demo.py!")  # Should appear in FileFilter
logger_instance.logger.critical("CRITICAL - ValueError occurred! This is a critical_issue!")  # Should appear in multiple filters

print("Log filtering demonstration complete!")