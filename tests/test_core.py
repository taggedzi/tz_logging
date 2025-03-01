import os
import sys
import pytest
import logging
from tz_logging.core import TzLogger, StreamHandlerConfig, RotatingFileHandlerConfig

@pytest.fixture
def logger_instance():
    """Fixture to create a fresh instance of TzLogger before each test."""
    return TzLogger("test_logger")

def test_logger_initialization(logger_instance):
    """Test that logger initializes with correct default values."""
    assert logger_instance.logger.name == "test_logger"
    assert logger_instance.logger.level == logging.DEBUG  # Default set to DEBUG
    assert logger_instance.logger.handlers == []  # Should start with no handlers

def test_add_stream_handler(logger_instance, capsys):
    """Test adding a stream handler and logging an INFO message."""
    console_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)
    logger_instance.add_stream_handler(console_config)

    assert len(logger_instance.logger.handlers) == 1
    assert isinstance(logger_instance.logger.handlers[0], logging.StreamHandler)

    logger_instance.logger.info("Test INFO message")
    captured = capsys.readouterr()
    assert "Test INFO message" in captured.out  # Verify log appears in console

def test_add_rotating_file_handler(logger_instance, tmp_path):
    """Test adding a rotating file handler and logging a message."""

    # Ensure the logger is clean before testing
    logger_instance.logger.handlers.clear()

    log_file = tmp_path / "test.log"
    file_config = RotatingFileHandlerConfig(file_path=str(log_file), max_bytes=1024, backup_count=1, level=logging.DEBUG)
    logger_instance.add_rotating_file_handler(file_config)

    assert len(logger_instance.logger.handlers) == 1
    assert isinstance(logger_instance.logger.handlers[0], logging.handlers.RotatingFileHandler)

    logger_instance.logger.debug("Test DEBUG message")

    with open(log_file, "r") as f:
        content = f.read()
    
    assert "Test DEBUG message" in content  # Verify log was written to file

def test_load_yaml_config(logger_instance, tmp_path):
    """Test loading configuration from a YAML file."""
    yaml_file = tmp_path / "logging.yaml"
    yaml_content = """
    version: 1
    disable_existing_loggers: False
    formatters:
      simple:
        format: "[%(levelname)s] %(message)s"
    handlers:
      console:
        class: logging.StreamHandler
        level: INFO
        formatter: simple
        stream: ext://sys.stdout
    root:
      level: INFO
      handlers: [console]
    """
    
    yaml_file.write_text(yaml_content)
    logger_instance.load_yaml_config(str(yaml_file))

    assert logger_instance.logger.level == logging.INFO
    assert logging.getLogger().level == logging.INFO  # Verify root logger level
    assert len(logger_instance.logger.handlers) == 1
    assert isinstance(logger_instance.logger.handlers[0], logging.StreamHandler)

def test_set_temporary_log_level_and_restore(logger_instance):
    """Test temporarily changing log level and restoring it."""
    console_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)
    logger_instance.add_stream_handler(console_config)

    original_level = logger_instance.logger.handlers[0].level

    logger_instance.set_temporary_log_level(logging.DEBUG)
    assert logger_instance.logger.handlers[0].level == logging.DEBUG  # Level should be updated

    logger_instance.restore_log_level()
    assert logger_instance.logger.handlers[0].level == original_level  # Should restore original level

def test_environment_variable_yaml_loading(monkeypatch, tmp_path):
    """Test loading YAML file via environment variable."""
    yaml_file = tmp_path / "env_logging.yaml"
    yaml_content = """
    version: 1
    disable_existing_loggers: False
    formatters:
      simple:
        format: "[%(levelname)s] %(message)s"
    handlers:
      console:
        class: logging.StreamHandler
        level: WARNING
        formatter: simple
        stream: ext://sys.stdout
    root:
      level: WARNING
      handlers: [console]
    """

    yaml_file.write_text(yaml_content)
    
    monkeypatch.setenv("TZ_LOGGING_CONFIG_FILE", str(yaml_file))
    logger_instance = TzLogger("env_test_logger")
    logger_instance.load_yaml_config()

    assert logger_instance.logger.level == logging.WARNING  # Ensures environment variable works
