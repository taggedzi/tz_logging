import logging
import re

class KeywordFilter(logging.Filter):
    """
    A filter that allows logging messages containing (positive) or excluding (negative) a given keyword or regex pattern.
    """
    def __init__(self, pattern: str, positive: bool = True, ignore_case: bool = True):
        """
        Initializes the filter.

        Args:
            pattern (str): The regex pattern to filter log messages.
            positive (bool): If True, only logs matching the pattern will be shown.
                            If False, logs matching the pattern will be hidden.
            ignore_case (bool): If True, makes the regex case-insensitive.
        """
        flags = re.IGNORECASE if ignore_case else 0
        self.regex = re.compile(pattern, flags)
        self.positive = positive

    def filter(self, record: logging.LogRecord) -> bool:
        """Filters log records based on the regex pattern."""
        message = record.getMessage()
        if not self.regex.flags & re.IGNORECASE:
            message = message.lower()
        match = self.regex.search(message)
        return bool(match) if self.positive else not bool(match)

# Test Script
if __name__ == "__main__":
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Testing the regex filter
    test_cases = [
        ("error|warning", True, True, [
            ("This is an error message", True),
            ("This is a warning", True),
            ("This is just info", False)
        ]),
        ("debug", False, False, [
            ("DEBUG: Something happened", False),
            ("This is an error message", True)
        ])
    ]
    
    for pattern, positive, ignore_case, cases in test_cases:
        print(f"\nTesting pattern: '{pattern}', positive: {positive}, ignore_case: {ignore_case}")
        filter = KeywordFilter(pattern, positive, ignore_case)
        console_handler.filters.clear()
        console_handler.addFilter(filter)
        
        for message, expected in cases:
            record = logging.LogRecord("test_logger", logging.INFO, "", 0, message, None, None)
            result = filter.filter(record)
            print(f"Message: '{message}' | Expected: {expected} | Result: {result}")
