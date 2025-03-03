import pytest
import logging
import os
import json
import time
from tz_logging.core import LogHandler, AsyncRemoteHandler, JSONFormatter
from logging.handlers import SysLogHandler

@pytest.fixture(autouse=True)
def clear_handlers():
    LogHandler._handler_registry.clear()

def test_log_filtering():
    handler = LogHandler("filter_test", output="console", include_filter="important", exclude_filter="debug")
    assert handler.filter(logging.LogRecord(name="test", level=logging.INFO, pathname=__file__, lineno=1, msg="This is important", args=(), exc_info=None))
    assert not handler.filter(logging.LogRecord(name="test", level=logging.INFO, pathname=__file__, lineno=1, msg="This is debug", args=(), exc_info=None))

def test_rolling_log_size():
    log_file = "test_rolling.log"
    handler = LogHandler("rolling_size_test", output=log_file, rolling_type="size", rolling_value=1024, backup_count=2)

    for _ in range(500):
        logging.info("Filling up rolling log file")

    assert os.path.exists(log_file)

    # **Fix: Close the handler before deleting the file**
    handler.handler.close()
    LogHandler._global_logger.removeHandler(handler.handler)
    os.remove(log_file)

def test_syslog_logging():
    syslog_address = ("localhost", 514)  # Ensure a valid address is passed
    handler = LogHandler("syslog_test", syslog_address=syslog_address)

    # **Fix: Check if the platform supports SysLogHandler**
    if isinstance(handler.handler, SysLogHandler):
        assert isinstance(handler.handler, SysLogHandler)
    else:
        print("[LOG HANDLER] Syslog not available on this platform. Skipping test.")

def test_live_config_reload():
    config_data = {
        "handlers": [{"name": "reload_test", "level": "INFO", "output": "console"}]
    }
    with open("test_config_reload.json", "w") as f:
        json.dump(config_data, f)
    LogHandler.load_from_config("test_config_reload.json")
    time.sleep(1)  # Simulate wait time for file watcher
    assert "reload_test" in LogHandler._handler_registry
    os.remove("test_config_reload.json")

if __name__ == "__main__":
    pytest.main()
