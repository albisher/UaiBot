#!/usr/bin/env python3
"""
Test runner for UaiBot tests.

This script runs all tests in the tests directory following Ubuntu test conventions.
"""

import os
import sys
import pytest
import logging
from uaibot.pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_test_environment():
    """Set up the test environment."""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Create test data directories if they don't exist
    test_data_dir = project_root / 'tests' / 'data'
    test_files_dir = test_data_dir / 'test_files'
    test_configs_dir = test_data_dir / 'test_configs'
    
    for directory in [test_data_dir, test_files_dir, test_configs_dir]:
        directory.mkdir(parents=True, exist_ok=True)

def run_tests():
    """Run the test suite."""
    try:
        # Set up test environment
        setup_test_environment()
        
        # Get test directory
        test_dir = Path(__file__).parent
        
        # Run tests with coverage
        args = [
            str(test_dir),
            '-v',
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html',
            '--cov-report=xml',
            '--junitxml=test-results.xml',
            '--html=test-report.html'
        ]
        
        # Add markers if specified
        if len(sys.argv) > 1:
            args.extend(sys.argv[1:])
            
        logger.info("Starting test execution...")
        result = pytest.main(args)
        
        if result == 0:
            logger.info("All tests passed successfully!")
        else:
            logger.error(f"Tests failed with exit code: {result}")
            
        return result
        
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests()) 