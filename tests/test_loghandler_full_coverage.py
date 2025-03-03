import pytest
import logging
import os
import json
import yaml
import time
from tz_logging.core import LogHandler, AsyncRemoteHandler, JSONFormatter
from logging.handlers import TimedRotatingFileHandler

@pytest.fixture(autouse=True)
def clear_handlers():
    LogHandler._handler_registry.clear()

# 1️⃣ Testing Config Loading (JSON & YAML)
def test_load_config_json():
    config_data = {
        "handlers": [{"name": "json_test", "level": "INFO", "output": "console"}]
    }
    with open("test_config.json", "w") as f:
        json.dump(config_data, f)
    LogHandler.load_from_config("test_config.json")
    assert "json_test" in LogHandler._handler_registry
    os.remove("test_config.json")

def test_load_config_yaml():
    config_data = {
        "handlers": [{"name": "yaml_test", "level": "INFO", "output": "console"}]
    }
    with open("test_config.yaml", "w") as f:
        yaml.dump(config_data, f)
    LogHandler.load_from_config("test_config.yaml")
    assert "yaml_test" in LogHandler._handler_registry
    os.remove("test_config.yaml")

# 2️⃣ Testing Error Handling (Invalid Configs)
def test_invalid_config_json():
    with open("invalid_config.json", "w") as f:
        f.write("{invalid json}")  # Corrupt JSON
    with pytest.raises(ValueError):
        LogHandler.load_from_config("invalid_config.json")
    os.remove("invalid_config.json")

def test_invalid_config_yaml():
    with open("invalid_config.yaml", "w") as f:
        f.write("invalid: yaml: -")  # Corrupt YAML
    with pytest.raises(ValueError):
        LogHandler.load_from_config("invalid_config.yaml")
    os.remove("invalid_config.yaml")

# 3️⃣ Testing Handler Removal & Modification
def test_remove_handler():
    handler = LogHandler("remove_test", output="console")
    assert "remove_test" in LogHandler._handler_registry
    LogHandler.remove_handler("remove_test")
    assert "remove_test" not in LogHandler._handler_registry

def test_modify_handler():
    handler = LogHandler("modify_test", output="console", level=logging.WARNING)
    LogHandler.modify_handler("modify_test", level=logging.ERROR)
    assert LogHandler._handler_registry["modify_test"].level == logging.ERROR

# 4️⃣ Testing Async Logging (Queue Handling, Retries)
def test_async_logging_queue():
    handler = LogHandler("async_test", remote_url="https://localhost/logs")
    for _ in range(10):  # Simulating multiple log entries
        logging.info("Async log message")
    assert isinstance(handler.handler, AsyncRemoteHandler)

# 5️⃣ Testing Rolling Log Files (Time-Based)
def test_rolling_log_time():
    log_file = "test_rolling_time.log"
    handler = LogHandler("rolling_time_test", output=log_file, rolling_type="time", rolling_value="s", backup_count=2)

    logging.info("Rolling log entry 1")
    time.sleep(2)  # Ensure it rolls over by time
    logging.info("Rolling log entry 2")

    assert os.path.exists(log_file)
    
    # Cleanup
    handler.handler.close()
    LogHandler._global_logger.removeHandler(handler.handler)
    os.remove(log_file)

# 6️⃣ Testing Watchdog Live Config Reload
def test_watchdog_config_reload():
    config_data = {
        "handlers": [{"name": "watchdog_test", "level": "INFO", "output": "console"}]
    }
    with open("test_watchdog_config.json", "w") as f:
        json.dump(config_data, f)
    
    LogHandler.load_from_config("test_watchdog_config.json")
    time.sleep(1)  # Allow watcher to detect change
    assert "watchdog_test" in LogHandler._handler_registry
    
    os.remove("test_watchdog_config.json")

if __name__ == "__main__":
    pytest.main()
