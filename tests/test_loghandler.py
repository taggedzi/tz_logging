import unittest
import logging
import os
import json
import yaml
from tz_logging.core import LogHandler, AsyncRemoteHandler, JSONFormatter

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
        print(f"Handler type: {type(handler.handler)}")  # Debugging line
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

if __name__ == "__main__":
    unittest.main()
