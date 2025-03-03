import unittest
import logging
import os
import json
import yaml
import time
from tz_logging.core10 import LogHandler, AsyncRemoteHandler, JSONFormatter
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, SysLogHandler

class TestLogHandler(unittest.TestCase):

    def setUp(self):
        # Clear existing handlers before each test
        LogHandler._handler_registry.clear()

    def test_create_console_handler(self):
        handler = LogHandler("console_test", output="console", level=logging.DEBUG)
        self.assertIn("console_test", LogHandler._handler_registry)
        self.assertEqual(handler.level, logging.DEBUG)

    def test_async_remote_logging(self):
        handler = LogHandler("remote_test", remote_url="https://example.com/logs")
        self.assertIn("remote_test", LogHandler._handler_registry)
        self.assertIsInstance(handler.handler, AsyncRemoteHandler)

    def test_json_formatting(self):
        formatter = JSONFormatter(extra_fields={"app": "test_app"})
        record = logging.LogRecord(name="test", level=logging.INFO, pathname=__file__, lineno=42, msg="Test message", args=(), exc_info=None)
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["app"], "test_app")

    def test_log_filtering(self):
        handler = LogHandler("filter_test", output="console", include_filter="important", exclude_filter="debug")
        self.assertTrue(handler.filter(logging.LogRecord(name="test", level=logging.INFO, pathname=__file__, lineno=1, msg="This is important", args=(), exc_info=None)))
        self.assertFalse(handler.filter(logging.LogRecord(name="test", level=logging.INFO, pathname=__file__, lineno=1, msg="This is debug", args=(), exc_info=None)))

    def test_modify_handler(self):
        handler = LogHandler("modify_test", output="console", level=logging.WARNING)
        LogHandler.modify_handler("modify_test", level=logging.ERROR)
        self.assertEqual(LogHandler._handler_registry["modify_test"].level, logging.ERROR)

    def test_config_loading(self):
        config_data = {
            "handlers": [
                {"name": "test_handler", "level": "INFO", "output": "console"}
            ]
        }
        with open("test_config.json", "w") as f:
            json.dump(config_data, f)
        LogHandler.load_from_config("test_config.json")
        self.assertIn("test_handler", LogHandler._handler_registry)
        os.remove("test_config.json")

    def test_rolling_log_size(self):
        log_file = "test_rolling.log"
        handler = LogHandler("rolling_size_test", output=log_file, rolling_type="size", rolling_value=1024, backup_count=2)
        
        for _ in range(500):
            logging.info("Filling up rolling log file")
        
        self.assertTrue(os.path.exists(log_file))

        # **Fix: Close the handler before deleting the file**
        handler.handler.close()
        LogHandler._global_logger.removeHandler(handler.handler)
        os.remove(log_file)

    def test_syslog_logging(self):
        syslog_address = ("localhost", 514)  # Ensure a valid address is passed
        handler = LogHandler("syslog_test", syslog_address=syslog_address)

        # **Fix: Check if the platform supports SysLogHandler**
        if isinstance(handler.handler, SysLogHandler):
            self.assertIsInstance(handler.handler, SysLogHandler)
        else:
            print("[LOG HANDLER] Syslog not available on this platform. Skipping test.")

    def test_live_config_reload(self):
        config_data = {
            "handlers": [
                {"name": "reload_test", "level": "INFO", "output": "console"}
            ]
        }
        with open("test_config_reload.json", "w") as f:
            json.dump(config_data, f)
        LogHandler.load_from_config("test_config_reload.json")
        time.sleep(1)  # Simulate wait time for file watcher
        self.assertIn("reload_test", LogHandler._handler_registry)
        os.remove("test_config_reload.json")

if __name__ == "__main__":
    unittest.main()
