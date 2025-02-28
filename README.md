# tz_logging - Simplifying Python Logging

As an experienced Python programmer, you know how powerful and versatile the built-in `logging` module is. However, setting up and configuring logging can be tedious, especially when dealing with non-terminal outputs or special conditions.

This project aims to simplify the process by providing a lightweight library that streamlines common use cases for logging in Python. The end goal of `tz_logging` is to facilitate quickly setting up and use logging without having to memorize complex options and configurations.

To make it even easier, I've included example scripts demonstrating basic examples on how to implement some of these solutions, so you won't have to spend time researching each case. My goal is to provide a convenient and flexible solution for handling logging in your Python projects.

I hope this helps!

## How to install

Coming soon. I hope to enter this into Pypi and allow installation as a `pip` package.

## How to use in a single script

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

## How to use in larger projects

In larger multi-file projects you can create an external script initiating your logger and call that into your other files to keep logging consistent. Here is a quick example:

```bash
my_project/
├── my_project/                  # Main package
│   ├── logging_config.py        # 🔥 Centralized logging setup
│   ├── core.py                  # Example module using logging
│   ├── utils.py                 # Another module using logging
├── scripts/                     # Optional scripts using logging
│   ├── run_app.py
├── logs/                        # Directory for log files
│   ├── app.log
├── tests/                       # Unit tests
├── setup.py
└── pyproject.toml
```

You could then define `logging_config.py` as something like this:

```python  
import logging
import sys
from .config import RotatingFileHandlerConfig, StreamHandlerConfig
from .core import TzLogger 

# Create the main logger instance
logger = TzLogger("my_project")

# Add a rotating file handler
file_config = RotatingFileHandlerConfig(file_path="logs/app.log", level=logging.DEBUG)
logger.add_rotating_file_handler(file_config)

# Add a stream handler for console output
stream_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)
logger.add_stream_handler(stream_config)

# Expose the logger for reuse
project_logger = logger.logger
```
Then in `my_project/core.py` you could do something like this:

```python
from .logging_config import project_logger

def core_function():
    project_logger.info("Core function executed")
```

Then for `my_project/utils.py`:

```python
from .logging_config import project_logger

def utility_function():
    project_logger.debug("Utility function running")
```

Then your scripts like `scripts/run_app.py` you could do something like this:

```python
from my_project.core import core_function
from my_project.utils import utility_function

core_function()
utility_function()
```

Now when you execute the script it will run the debug across all the files that use your `my_project/logging_config.py` file. In this case logging all messages from DEBUG and up to the file `logs/app.log` AND all messages INFO and up to the terminal.

## Notes

This can be highly customized and configured. You can add multiple streams to output different levels of logging. Including outputing to files, with options for file size limits, max number of files allowed, and output formats.

## Useful Links

* [LogRecord Attributes] (https://docs.python.org/3/library/logging.html#logrecord-objects): Useful for accessing all the information available to you when creating the output for error messages.