import pytest
import logging
import os
import json
import yaml
from tz_logging.core import LogHandler, AsyncRemoteHandler, JSONFormatter

@pytest.fixture(autouse=True)
def clear_handlers():
    LogHandler._handler_registry.clear()

def test_create_console_handler():
    handler = LogHandler("console_test", output="console", level=logging.DEBUG)
    assert "console_test" in LogHandler._handler_registry
    assert handler.level == logging.DEBUG

def test_async_remote_logging():
    handler = LogHandler("remote_test", remote_url="https://example.com/logs")
    assert "remote_test" in LogHandler._handler_registry
    assert isinstance(handler.handler, AsyncRemoteHandler)

def test_json_formatting():
    formatter = JSONFormatter(extra_fields={"app": "test_app"})
    record = logging.LogRecord(name="test", level=logging.INFO, pathname=__file__, lineno=42, msg="Test message", args=(), exc_info=None)
    formatted = formatter.format(record)
    log_data = json.loads(formatted)
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"
    assert log_data["app"] == "test_app"

def test_modify_handler():
    handler = LogHandler("modify_test", output="console", level=logging.WARNING)
    LogHandler.modify_handler("modify_test", level=logging.ERROR)
    assert LogHandler._handler_registry["modify_test"].level == logging.ERROR

def test_config_loading():
    config_data = {
        "handlers": [{"name": "test_handler", "level": "INFO", "output": "console"}]
    }
    with open("test_config.json", "w") as f:
        json.dump(config_data, f)
    LogHandler.load_from_config("test_config.json")
    assert "test_handler" in LogHandler._handler_registry
    os.remove("test_config.json")

if __name__ == "__main__":
    pytest.main()
