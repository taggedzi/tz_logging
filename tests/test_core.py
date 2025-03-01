import os
import sys
import pytest
import logging
import yaml
from unittest import mock
from tz_logging.core import TzLogger, StreamHandlerConfig, RotatingFileHandlerConfig

# Define a simple dummy filter for testing
class DummyFilter(logging.Filter):
    def filter(self, record):
        return True

@pytest.fixture
def logger_instance():
    """Fixture to create a fresh TzLogger instance with no handlers."""
    logger = TzLogger("test_logger")
    return logger

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

def test_restore_log_level_no_previous_changes(capfd):
    """
    Test calling restore_log_level when no temporary changes were made.
    It should hit the else block and print: "No previous log level stored. Nothing to restore."
    """
    logger = TzLogger("test_logger")

    # Ensure _original_levels is empty
    assert not logger._original_levels, "Expected _original_levels to be empty before calling restore_log_level"

    # Call restore_log_level without prior temporary log level change
    logger.restore_log_level()

    # Capture printed output
    captured = capfd.readouterr()
    assert "No previous log level stored. Nothing to restore." in captured.out, f"Unexpected output: {captured.out}"

    # Ensure _original_levels is still empty after calling restore_log_level
    assert not logger._original_levels, "Expected _original_levels to remain empty after restore_log_level"


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

def test_load_yaml_config_invalid_yaml(logger_instance, tmp_path):
    """
    Test that loading an invalid YAML configuration file raises a yaml.YAMLError.
    
    This test writes invalid YAML content to a temporary file and then verifies that
    TzLogger.load_yaml_config() raises a yaml.YAMLError when attempting to load it.
    """
    # Create an invalid YAML file in the temporary directory.
    invalid_yaml_file = tmp_path / "invalid.yaml"
    # Write invalid YAML content (this syntax is purposely broken).
    invalid_yaml_file.write_text("this: is: not: valid: yaml: :::")
    
    with pytest.raises(yaml.YAMLError):
        # Expect a yaml.YAMLError to be raised due to invalid syntax.
        logger_instance.load_yaml_config(str(invalid_yaml_file))

def test_load_nonexistent_yaml():
    """Test loading a nonexistent YAML file."""
    logger = TzLogger("test_logger")
    with pytest.raises(FileNotFoundError):
        logger.load_yaml_config("does_not_exist.yaml")


def test_set_and_restore_temporary_log_level(logger_instance):
    """
    Test that set_temporary_log_level and restore_log_level work as expected.
    
    The test will:
      1. Attach a stream handler with an initial level of INFO.
      2. Call set_temporary_log_level(DEBUG) and verify that the handler's level becomes DEBUG.
      3. Call restore_log_level() and verify that the handler's level reverts to INFO.
    """
    # Step 1: Add a stream handler with level INFO
    stream_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)
    handler = logger_instance.add_stream_handler(stream_config)
    
    # Confirm the initial level is INFO (20)
    original_level = handler.level
    assert original_level == logging.INFO, "Initial handler level should be INFO"
    
    # Step 2: Temporarily change the log level to DEBUG (10)
    logger_instance.set_temporary_log_level(logging.DEBUG)
    assert handler.level == logging.DEBUG, "Handler level should be DEBUG after temporary change"
    
    # Step 3: Restore the original log level
    logger_instance.restore_log_level()
    assert handler.level == original_level, "Handler level should be restored to INFO after calling restore_log_level()"

def test_invalid_log_file_path(tmp_path):
    """Test setting an invalid file path for logging."""
    logger = TzLogger("test_logger")
    invalid_path = tmp_path / "nonexistent_dir" / "app.log"  # Create a fake path

    config = RotatingFileHandlerConfig(file_path=str(invalid_path))

    with pytest.raises(FileNotFoundError):  # Expect failure when trying to write
        logger.add_rotating_file_handler(config)

def test_missing_formatter():
    """Test adding a handler without a formatter."""
    logger = TzLogger("test_logger")

    with pytest.raises(ValueError, match="StreamHandlerConfig is required"):
        logger.add_stream_handler(None)  # Should fail before adding to logger

def test_unwritable_log_directory(monkeypatch, tmp_path):
    """Test adding a rotating file handler to a non-writable directory by simulating insufficient permissions."""
    logger = TzLogger("test_logger")
    log_dir = tmp_path / "protected"
    log_dir.mkdir()
    
    # Use monkeypatch to simulate that the directory is not writable.
    # For the specific directory, return False regardless of the actual permissions.
    original_access = os.access  # Save the original os.access
    def fake_access(path, mode):
        if os.path.abspath(path) == os.path.abspath(str(log_dir)):
            return False
        return original_access(path, mode)
    
    monkeypatch.setattr(os, "access", fake_access)
    
    config = RotatingFileHandlerConfig(file_path=str(log_dir / "app.log"))
    
    with pytest.raises(PermissionError, match="Cannot write to log directory"):
        logger.add_rotating_file_handler(config)

def test_add_filter(logger_instance):
    """
    Test that add_filter correctly attaches the given filter to all handlers.
    
    1. A stream handler is added to the logger.
    2. A DummyFilter is created and added using add_filter.
    3. The test verifies that the dummy filter is present in each handler's filter list.
    """
    # Step 1: Create and add a stream handler with a specific configuration
    stream_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)
    handler = logger_instance.add_stream_handler(stream_config)
    
    # Ensure the handler starts with no filters
    assert len(handler.filters) == 0, "Handler should initially have no filters."
    
    # Step 2: Create a dummy filter and add it using the add_filter method
    dummy_filter = DummyFilter("dummy")
    logger_instance.add_filter(dummy_filter)
    
    # Step 3: Check that the dummy filter is now attached to all handlers in the logger
    for h in logger_instance.logger.handlers:
        assert dummy_filter in h.filters, "DummyFilter was not added to handler filters."

def test_stream_handler_config_repr():
    """Test the __repr__ method of StreamHandlerConfig."""
    config = StreamHandlerConfig(stream=sys.stdout, level=logging.DEBUG, format_str="%(message)s")
    actual_repr = repr(config)

    # Ensure the representation contains key attributes (but ignore stream object details)
    assert "StreamHandlerConfig(stream=" in actual_repr, f"Unexpected __repr__: {actual_repr}"
    assert "level=10" in actual_repr, f"Expected log level in __repr__, got: {actual_repr}"
    assert "format_str=%(message)s" in actual_repr, f"Expected format_str in __repr__, got: {actual_repr}"