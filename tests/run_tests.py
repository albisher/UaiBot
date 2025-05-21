#!/usr/bin/env python3
"""
Test runner for UaiBot project.
Runs all tests in the test directory using pytest.
"""

import os
import sys
import pytest
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Set up test environment
    os.environ['PYTHONPATH'] = str(project_root)
    
    # Run tests
    test_dir = Path(__file__).parent
    pytest.main([
        str(test_dir),
        '-v',
        '--tb=short',
        '--cov=uaibot',
        '--cov-report=term-missing',
        '--cov-report=html:test/results/coverage'
    ])

if __name__ == '__main__':
    main() 