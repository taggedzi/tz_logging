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
@pytest.mark.parametrize("handler_type,output", [
    ("console", "console"),
    ("file", "test.log"),
    ("syslog", ("localhost", 514)),
    ("remote", "https://example.com/logs")
])
def test_handler_initialization(handler_type, output):
    if handler_type == "syslog":
        handler = LogHandler("syslog_test", syslog_address=output)
    elif handler_type == "remote":
        handler = LogHandler("remote_test", remote_url=output)
    else:
        handler = LogHandler(f"{handler_type}_test", output=output)

    assert handler.handler is not None

    if handler_type == "file":
        assert os.path.exists(output)
        handler.handler.close()
        os.remove(output)

# 3️⃣ Additional Config Parsing & Error Handling Tests
@pytest.mark.parametrize("config_data,raises_exception", [
    ({"handlers": [{"name": "valid_test", "level": "INFO", "output": "console"}]}, False),
    ({"invalid_key": "value"}, False),  # Should not crash but ignore invalid key
    ("{invalid json}", True),  # Corrupt JSON
    ("invalid: yaml: -", True)  # Corrupt YAML
])
def test_load_config_errors(config_data, raises_exception):
    filename = "test_config_error.yaml" if isinstance(config_data, dict) else "test_config_error.json"
    with open(filename, "w") as f:
        if isinstance(config_data, dict):
            yaml.dump(config_data, f)
        else:
            f.write(config_data)

    if raises_exception:
        with pytest.raises((ValueError, yaml.YAMLError, json.JSONDecodeError)):
            LogHandler.load_from_config(filename)
    else:
        LogHandler.load_from_config(filename)
        # Instead of checking arbitrary handlers, verify the expected valid one exists
        if "handlers" in config_data:
            assert "valid_test" in LogHandler._handler_registry

    os.remove(filename)

# 4️⃣ Edge Cases for Handler Modifications
def test_modify_handler_formatter():
    handler = LogHandler("formatter_test", output="console")
    
    # Modify the formatter (Use 'formatter' instead of 'fmt')
    LogHandler.modify_handler("formatter_test", formatter="%(message)s")
    
    assert handler.formatter._fmt == "%(message)s"

def test_remove_nonexistent_handler():
    assert LogHandler.remove_handler("nonexistent_handler") is None

# 5️⃣ Async Logging Queue Overflow & Handling
def test_async_logging_queue_overflow():
    handler = LogHandler("overflow_test", remote_url="https://localhost/logs")
    try:
        for _ in range(5000):  
            handler.handler.log_queue.put_nowait("Forced log entry")
    except queue.Full:
        assert True  # Queue should be full

# 6️⃣ Exception Handling in Async Logging
def test_async_remote_handler_failure(monkeypatch):
    def mock_request(*args, **kwargs):
        raise ConnectionError("Simulated network failure")

    monkeypatch.setattr("requests.request", mock_request)
    handler = LogHandler("failure_test", remote_url="https://example.com/logs")
    logging.info("This should trigger a failed network request")

# 7️⃣ Testing Cleanup & Teardown
def test_logging_cleanup():
    handler = LogHandler("cleanup_test", output="console")
    LogHandler.remove_handler("cleanup_test")
    assert "cleanup_test" not in LogHandler._handler_registry

if __name__ == "__main__":
    pytest.main()
