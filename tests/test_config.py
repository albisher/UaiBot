"""
Test configuration for UaiBot tests.

This module contains configuration settings for test execution.
"""

import os
import logging

# Test environment settings
TEST_ENV = {
    'PYTHONPATH': os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
    'TESTING': 'true',
    'LOG_LEVEL': 'DEBUG'
}

# Test logging configuration
TEST_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': 'test.log',
            'mode': 'w'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

# Test data paths
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

# Test timeout settings (in seconds)
TEST_TIMEOUTS = {
    'unit_test': 5,
    'integration_test': 30,
    'system_test': 120
}

# Test coverage settings
COVERAGE_CONFIG = {
    'source': ['app'],
    'omit': [
        '*/tests/*',
        '*/migrations/*',
        '*/__init__.py',
        '*/settings.py'
    ],
    'branch': True,
    'fail_under': 80
}

def setup_test_environment():
    """Set up the test environment."""
    # Set environment variables
    for key, value in TEST_ENV.items():
        os.environ[key] = str(value)
    
    # Configure logging
    logging.config.dictConfig(TEST_LOGGING)
    
    # Create test data directory if it doesn't exist
    if not os.path.exists(TEST_DATA_DIR):
        os.makedirs(TEST_DATA_DIR) 