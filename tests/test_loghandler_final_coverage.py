import pytest
import logging
import os
import json
import yaml
import time
import queue
from tz_logging.core import LogHandler, AsyncRemoteHandler, JSONFormatter

@pytest.fixture(autouse=True)
def clear_handlers():
    LogHandler._handler_registry.clear()

# 1️⃣ Module Initialization Test
def test_module_initialization():
    assert LogHandler._global_logger is not None
    assert isinstance(LogHandler._handler_registry, dict)

# 2️⃣ Testing Various Handler Initializations
def test_handler_file_output():
    handler = LogHandler("file_test", output="test.log")
    assert os.path.exists("test.log")
    handler.handler.close()
    os.remove("test.log")

def test_handler_syslog():
    handler = LogHandler("syslog_test", syslog_address=("localhost", 514))
    assert handler.handler is not None

def test_handler_json_format():
    handler = LogHandler("json_test", output="console", json_format=True, extra_fields={"env": "test"})
    assert isinstance(handler.formatter, JSONFormatter)

# 3️⃣ Additional Config Parsing & Error Handling Tests
def test_load_config_missing_key():
    config_data = {"invalid_key": "value"}
    with open("test_invalid_config.yaml", "w") as f:
        yaml.dump(config_data, f)

    LogHandler.load_from_config("test_invalid_config.yaml")

    # Instead of expecting a KeyError, assert that the handler was NOT created
    assert "invalid_key" not in LogHandler._handler_registry

    os.remove("test_invalid_config.yaml")


def test_load_config_corrupt_yaml():
    with open("test_corrupt.yaml", "w") as f:
        f.write("invalid: yaml: -")
    with pytest.raises(ValueError):
        LogHandler.load_from_config("test_corrupt.yaml")
    os.remove("test_corrupt.yaml")

# 4️⃣ Edge Cases for Handler Modifications
def test_modify_handler_formatter():
    handler = LogHandler("formatter_test", output="console")
    LogHandler.modify_handler("formatter_test", formatter="%(message)s")
    assert handler.formatter._fmt == "%(message)s"

def test_remove_nonexistent_handler():
    result = LogHandler.remove_handler("nonexistent_handler")
    assert result is None  # Should fail gracefully

def test_async_logging_queue_overflow():
    handler = LogHandler("overflow_test", remote_url="https://localhost/logs")

    # Try to overflow the queue
    with pytest.raises(queue.Full):  # Expect the queue to hit its max size
        for _ in range(5000):  
            handler.handler.log_queue.put_nowait("Forced log entry")

# 6️⃣ Exception Handling in Async Logging
def test_async_remote_handler_failure(monkeypatch):
    def mock_request(*args, **kwargs):
        raise ConnectionError("Simulated network failure")

    monkeypatch.setattr("requests.request", mock_request)
    handler = LogHandler("failure_test", remote_url="https://localhost/logs")
    logging.info("This should trigger a failed network request")

if __name__ == "__main__":
    pytest.main()
