# tz_logging - Simplifying Python Logging

As an experienced Python programmer, you know how powerful and versatile the built-in `logging` module is. However, setting up and configuring logging can be tedious, especially when dealing with non-terminal outputs or special conditions.

This project aims to simplify the process by providing a lightweight library that streamlines common use cases for logging in Python. The end goal of tz_logging is to facilitate quickly setting up and use logging without having to memorize complex options and configurations.

To make it even easier, I've included example scripts demonstrating basic examples on how to implement some of these solutions, so you won't have to spend time researching each case. My goal is to provide a convenient and flexible solution for handling logging in your Python projects.

I hope this helps!

## How to install

Coming soon. I hope to enter this into Pypi and allow installation as a `pip` package.

## How to use

You can look at the `examples` folder in this repository for specific use cases. But in the simplest terms here is how you can include `tz_logging` and use it in a script

```python
# Import the library
from tz_logging.core import TzLogger, StreamHandlerConfig

# Initialize the logger
my_log = TzLogger("my_log")
# Add a stream handler -> This is configurable (see examples)
my_log.add_stream_handler(StreamHandlerConfig())

# Use like python's logging 
my_log.logger.info("Info Test run")
my_log.logger.debug("Debug Test run")
my_log.logger.warning("Warning Test run")
my_log.logger.error("Error Test run")
```

## Notes

This can be highly customized and configured. You can add multiple streams to output different levels of logging. Including outputing to files, with options for file size limits, max number of files allowed, and output formats.
