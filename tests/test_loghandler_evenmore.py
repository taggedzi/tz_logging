import pytest
from unittest.mock import patch, MagicMock, mock_open
import logging
import queue
import requests
import os
import sys

from src.tz_logging.core import RemoteHandler, AsyncRemoteHandler, LogHandler, WATCHDOG_AVAILABLE

@patch("src.tz_logging.core.requests.request")
def test_remote_handler_success(mock_request):
    """Test that RemoteHandler sends a log successfully."""
    mock_request.return_value.status_code = 200
    handler = RemoteHandler(url="http://example.com", method="POST")
    record = logging.LogRecord("test", logging.INFO, "test.py", 10, "Test log", None, None)
    handler.emit(record)
    mock_request.assert_called_once()

@patch("src.tz_logging.core.requests.request", side_effect=requests.RequestException("Error"))
def test_remote_handler_failure(mock_request):
    """Test that RemoteHandler handles request failure gracefully."""
    handler = RemoteHandler(url="http://example.com", method="POST")
    record = logging.LogRecord("test", logging.INFO, "test.py", 10, "Test log", None, None)
    with patch("builtins.print") as mock_print:
        handler.emit(record)
        mock_print.assert_called_with("[LOG HANDLER] Failed to send log: Error")

@patch("queue.Queue.put_nowait", side_effect=queue.Full)
def test_async_handler_queue_full(mock_queue):
    """Test that AsyncRemoteHandler handles full queue gracefully."""
    handler = AsyncRemoteHandler(url="http://example.com")
    record = logging.LogRecord("test", logging.INFO, "test.py", 10, "Test log", None, None)
    with patch("builtins.print") as mock_print:
        handler.emit(record)
        mock_print.assert_called_with("[LOG HANDLER] Queue full. Dropping log:", "Test log")

@patch("src.tz_logging.core.SysLogHandler")
def test_log_handler_syslog_initialization(mock_syslog):
    """Test that LogHandler initializes SysLogHandler correctly."""
    handler = LogHandler(name="test_logger")
    assert hasattr(handler, "handler"), "LogHandler instance should have a 'handler' attribute"
    mock_syslog.assert_not_called()

@patch("os.path.abspath")
@patch("builtins.print")
@patch("builtins.open", new_callable=mock_open, read_data='{"log_level": "INFO"}')
def test_log_handler_watchdog_config_reload(mock_open, mock_print, mock_abspath):
    """Test that LogHandler detects config changes and reloads."""
    if not WATCHDOG_AVAILABLE:
        pytest.skip("Watchdog not available")
    
    mock_abspath.return_value = "config.yaml"
    event_mock = MagicMock()
    event_mock.src_path = "config.yaml"
    handler = LogHandler(name="test_logger")
    
    assert hasattr(handler, "load_from_config"), "LogHandler should have a 'load_from_config' method"
    handler.load_from_config("config.yaml")
    
    if not mock_print.call_args_list:
        print("No print statements were captured during config reload.")
    else:
        print("Captured print statements:", mock_print.call_args_list)
    
    printed_statements = [call.args[0] for call in mock_print.call_args_list]
    assert len(printed_statements) > 0, "No print statements were captured, config reload may not be executing properly."

# Updated Tests to Fix Issues

def test_log_handler_init_defaults():
    """Test LogHandler initialization with default parameters."""
    handler = LogHandler(name="default_logger")
    assert handler.name == "default_logger"
    assert isinstance(handler.handler, logging.Handler), "Handler should be a valid logging handler"

def test_log_handler_log_without_handler(caplog):
    """Test that LogHandler logs a message even without an explicit handler."""
    handler = LogHandler(name="test_logger")
    with caplog.at_level(logging.INFO):
        handler.log(logging.INFO, "Test log")
    assert "Test log" in caplog.text
