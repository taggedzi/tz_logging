"""This file contains the dataclass classes used for configuring the logger.
"""
from dataclasses import dataclass
import logging
from typing import Optional
import sys


@dataclass
class RotatingFileHandlerConfig:
    """Config for for rotating file handler.
    """
    file_path: str
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    level: int = logging.INFO
    format_str: Optional[str] = None

@dataclass
class StreamHandlerConfig:
    def __init__(self, stream=sys.stdout, level=logging.INFO, format_str=None):
        self.stream = stream
        self.level = level
        self.format_str = format_str

    def __repr__(self):
        return f"StreamHandlerConfig(stream={self.stream}, level={self.level}, format_str={self.format_str})"

