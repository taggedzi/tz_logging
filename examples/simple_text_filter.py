import logging
from tz_logging.core import LogHandler

# Initialize the logger
text_filtering = LogHandler("text_filtering")

# Add a keyword filter to the handler -> Only one keyword filter per handler But can be regex.
text_filtering.set_keyword_filter(search_text="CRITICAL FAILURE")

logging.info("This is an INFO message.")   # Will be filtered out
logging.error("This is an ERROR message.")  # Will be filtered out
logging.critical("This is a CRITICAL FAILURE message.")  # Will be shown
logging.critical("This is a CRITICAL message.")  # Will be filtered

text_filtering.set_keyword_filter("ERROR|CRITICAL FAILURE", positive=False)

logging.info("This is an INFO message.")   # Will be Shown
logging.error("This is an ERROR message.")  # Will be filtered out
logging.critical("This is a CRITICAL FAILURE message.")  # Will be shown
logging.critical("This is a CRITICAL message.")  # Will be Shown
