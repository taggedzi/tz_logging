import os
import sys
import pytest
import logging
import yaml
from tz_logging.core import TzLogger, StreamHandlerConfig, RotatingFileHandlerConfig


class DummyFilter(logging.Filter):
    """A simple dummy filter for testing logging filters."""
    def filter(self, record: logging.LogRecord) -> bool:
        return True


@pytest.fixture
def logger_instance() -> TzLogger:
    """
    Fixture to create a fresh TzLogger instance with no handlers.
    
    Returns:
        TzLogger: A new instance of TzLogger with the name 'test_logger'.
    """
    return TzLogger("test_logger")


def test_logger_initialization(logger_instance: TzLogger) -> None:
    """
    Test that the logger initializes with correct default values.
    
    Verifies that the logger name, level, and handlers list are as expected.
    """
    assert logger_instance.logger.name == "test_logger"
    assert logger_instance.logger.level == logging.DEBUG  # Default set to DEBUG
    assert logger_instance.logger.handlers == []  # Should start with no handlers


def test_add_stream_handler(logger_instance: TzLogger, capsys) -> None:
    """
    Test adding a stream handler and logging an INFO message.
    
    Ensures that after adding a stream handler, messages logged at INFO level appear in the console.
    """
    console_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)
    logger_instance.add_stream_handler(console_config)

    assert len(logger_instance.logger.handlers) == 1
    assert isinstance(logger_instance.logger.handlers[0], logging.StreamHandler)

    logger_instance.logger.info("Test INFO message")
    captured = capsys.readouterr()
    assert "Test INFO message" in captured.out  # Verify log appears in console


def test_add_rotating_file_handler(logger_instance: TzLogger, tmp_path) -> None:
    """
    Test adding a rotating file handler and logging a message.
    
    Verifies that a RotatingFileHandler is correctly added and that logged messages are written to the file.
    """
    # Ensure the logger is clean before testing
    logger_instance.logger.handlers.clear()

    log_file = tmp_path / "test.log"
    file_config = RotatingFileHandlerConfig(
        file_path=str(log_file),
        max_bytes=1024,
        backup_count=1,
        level=logging.DEBUG
    )
    logger_instance.add_rotating_file_handler(file_config)

    assert len(logger_instance.logger.handlers) == 1
    assert isinstance(logger_instance.logger.handlers[0], logging.handlers.RotatingFileHandler)

    logger_instance.logger.debug("Test DEBUG message")

    with open(log_file, "r") as f:
        content = f.read()
    
    assert "Test DEBUG message" in content  # Verify log was written to file


def test_load_yaml_config(logger_instance: TzLogger, tmp_path) -> None:
    """
    Test loading a YAML configuration file.
    
    Writes a temporary YAML config file, loads it, and verifies that the logger and root logger
    levels are updated as specified in the configuration.
    """
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


def test_set_temporary_log_level_and_restore(logger_instance: TzLogger) -> None:
    """
    Test temporarily changing the log level and restoring it.
    
    Adds a stream handler, changes its log level to DEBUG temporarily, and then restores it.
    """
    console_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)
    logger_instance.add_stream_handler(console_config)

    original_level = logger_instance.logger.handlers[0].level

    logger_instance.set_temporary_log_level(logging.DEBUG)
    assert logger_instance.logger.handlers[0].level == logging.DEBUG

    logger_instance.restore_log_level()
    assert logger_instance.logger.handlers[0].level == original_level


def test_restore_log_level_no_previous_changes(capfd) -> None:
    """
    Test calling restore_log_level when no temporary changes were made.
    
    Verifies that calling restore_log_level without prior changes prints the expected message
    and leaves the _original_levels dictionary empty.
    """
    logger = TzLogger("test_logger")
    # Ensure _original_levels is empty
    assert not logger._original_levels, "Expected _original_levels to be empty before calling restore_log_level"

    logger.restore_log_level()
    captured = capfd.readouterr()
    assert "No previous log level stored. Nothing to restore." in captured.out, f"Unexpected output: {captured.out}"
    assert not logger._original_levels, "Expected _original_levels to remain empty after restore_log_level"


def test_environment_variable_yaml_loading(monkeypatch, tmp_path) -> None:
    """
    Test loading a YAML file via an environment variable.
    
    Sets the TZ_LOGGING_CONFIG_FILE environment variable and verifies that the logger is configured accordingly.
    """
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
    logger_instance_env = TzLogger("env_test_logger")
    logger_instance_env.load_yaml_config()

    assert logger_instance_env.logger.level == logging.WARNING  # Ensures environment variable works


def test_load_yaml_config_invalid_yaml(logger_instance: TzLogger, tmp_path) -> None:
    """
    Test that loading an invalid YAML configuration file raises a yaml.YAMLError.
    
    Writes an invalid YAML file and confirms that a yaml.YAMLError is raised.
    """
    invalid_yaml_file = tmp_path / "invalid.yaml"
    invalid_yaml_file.write_text("this: is: not: valid: yaml: :::")
    
    with pytest.raises(yaml.YAMLError):
        logger_instance.load_yaml_config(str(invalid_yaml_file))


def test_load_nonexistent_yaml() -> None:
    """
    Test loading a nonexistent YAML configuration file.
    
    Confirms that a FileNotFoundError is raised when the specified file does not exist.
    """
    logger = TzLogger("test_logger")
    with pytest.raises(FileNotFoundError):
        logger.load_yaml_config("does_not_exist.yaml")


def test_set_and_restore_temporary_log_level(logger_instance: TzLogger) -> None:
    """
    Test that set_temporary_log_level and restore_log_level work as expected.
    
    Attaches a stream handler with level INFO, changes it to DEBUG, and then restores it.
    """
    stream_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)
    handler = logger_instance.add_stream_handler(stream_config)
    
    original_level = handler.level
    assert original_level == logging.INFO, "Initial handler level should be INFO"
    
    logger_instance.set_temporary_log_level(logging.DEBUG)
    assert handler.level == logging.DEBUG, "Handler level should be DEBUG after temporary change"
    
    logger_instance.restore_log_level()
    assert handler.level == original_level, "Handler level should be restored to INFO after calling restore_log_level()"


def test_invalid_log_file_path(tmp_path) -> None:
    """
    Test setting an invalid file path for logging.
    
    Attempts to add a rotating file handler with a non-existent directory and confirms that FileNotFoundError is raised.
    """
    logger = TzLogger("test_logger")
    invalid_path = tmp_path / "nonexistent_dir" / "app.log"
    config = RotatingFileHandlerConfig(file_path=str(invalid_path))
    
    with pytest.raises(FileNotFoundError):
        logger.add_rotating_file_handler(config)


def test_missing_formatter() -> None:
    """
    Test adding a stream handler with a missing formatter.
    
    Ensures that passing None to add_stream_handler raises a ValueError.
    """
    logger = TzLogger("test_logger")
    
    with pytest.raises(ValueError, match="StreamHandlerConfig is required"):
        logger.add_stream_handler(None)


def test_unwritable_log_directory(monkeypatch, tmp_path) -> None:
    """
    Test adding a rotating file handler to a non-writable directory.
    
    Simulates a directory with insufficient write permissions and confirms that a PermissionError is raised.
    """
    logger = TzLogger("test_logger")
    log_dir = tmp_path / "protected"
    log_dir.mkdir()
    
    original_access = os.access  # Save the original os.access function
    
    def fake_access(path, mode):
        if os.path.abspath(path) == os.path.abspath(str(log_dir)):
            return False
        return original_access(path, mode)
    
    monkeypatch.setattr(os, "access", fake_access)
    config = RotatingFileHandlerConfig(file_path=str(log_dir / "app.log"))
    
    with pytest.raises(PermissionError, match="Cannot write to log directory"):
        logger.add_rotating_file_handler(config)


def test_add_filter(logger_instance: TzLogger) -> None:
    """
    Test that add_filter correctly attaches the given filter to all handlers.
    
    Adds a stream handler, then a DummyFilter, and verifies that the filter is attached to each handler.
    """
    stream_config = StreamHandlerConfig(stream=sys.stdout, level=logging.INFO)
    handler = logger_instance.add_stream_handler(stream_config)
    assert len(handler.filters) == 0, "Handler should initially have no filters."
    
    dummy_filter = DummyFilter("dummy")
    logger_instance.add_filter(dummy_filter)
    
    for h in logger_instance.logger.handlers:
        assert dummy_filter in h.filters, "DummyFilter was not added to handler filters."


def test_stream_handler_config_repr() -> None:
    """
    Test the __repr__ method of StreamHandlerConfig.
    
    Verifies that the string representation contains key attributes.
    """
    config = StreamHandlerConfig(stream=sys.stdout, level=logging.DEBUG, format_str="%(message)s")
    actual_repr = repr(config)
    
    assert "StreamHandlerConfig(stream=" in actual_repr, f"Unexpected __repr__: {actual_repr}"
    assert "level=10" in actual_repr, f"Expected log level in __repr__, got: {actual_repr}"
    assert "format_str=%(message)s" in actual_repr, f"Expected format_str in __repr__, got: {actual_repr}"
