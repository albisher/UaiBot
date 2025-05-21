"""
Configuration settings for UaiBot test sequence.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
LOG_DIR = PROJECT_ROOT / 'log'
TEST_DIR = PROJECT_ROOT / 'test'
SCREENSHOT_DIR = TEST_DIR / 'screenshots'
REPORT_DIR = TEST_DIR / 'reports'

# Test settings
DEFAULT_WAIT_TIME = 2  # seconds
BROWSER_WAIT_TIME = 5  # seconds
SCREENSHOT_CONFIDENCE = 0.8

# Browser settings
SUPPORTED_BROWSERS = [
    "chrome",
    "firefox",
    "safari",
    "edge"
]

# Test sequence settings
SEQUENCE_RETRY_COUNT = 3
SEQUENCE_RETRY_DELAY = 2  # seconds

# Create necessary directories
for directory in [LOG_DIR, TEST_DIR, SCREENSHOT_DIR, REPORT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Logging configuration
LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'sequence_test.log'),
            'formatter': 'standard',
            'level': 'INFO',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Test result status codes
class TestStatus:
    SUCCESS = 'success'
    FAILURE = 'failure'
    ERROR = 'error'
    SKIPPED = 'skipped'
    PENDING = 'pending' 