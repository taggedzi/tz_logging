"""This file contains the dataclass classes used for configuring the logger.
"""
from dataclasses import dataclass
import logging
from typing import Optional, TextIO
import sys


@dataclass
class RotatingFileHandlerConfig:
    """Config for for rotating file handler.
    """
    file_path: str
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    level: int = logging.DEBUG
    format_str: Optional[str] = None

@dataclass
class StreamHandlerConfig:
    """config for stream handler
    """
    stream: TextIO = sys.stdout
    level: int = logging.INFO
    format_str: Optional[str] = None
