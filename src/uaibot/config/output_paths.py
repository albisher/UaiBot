"""
Configuration for all output paths and logging in UaiBot.
This ensures consistent output locations across the application.
"""
import os
from pathlib import Path
from datetime import datetime

# Base directories
ROOT_DIR = Path(__file__).parent.parent.parent
TEST_FILES_DIR = ROOT_DIR / "test_files"
LOGS_DIR = ROOT_DIR / "logs"
OUTPUT_DIR = ROOT_DIR / "tests" / "results"

# Test-related directories
TEST_COVERAGE_DIR = OUTPUT_DIR / "coverage"
TEST_LOGS_DIR = LOGS_DIR / "tests"
TEST_OUTPUTS_DIR = OUTPUT_DIR / "outputs"

# Application-specific directories
APP_LOGS_DIR = LOGS_DIR / "uaibot"
CACHE_DIR = ROOT_DIR / "uaibot" / "cache"
DATA_DIR = ROOT_DIR / "uaibot" / "data"

def ensure_directories():
    """Create all necessary directories if they don't exist."""
    directories = [
        TEST_FILES_DIR,
        LOGS_DIR,
        OUTPUT_DIR,
        TEST_COVERAGE_DIR,
        TEST_LOGS_DIR,
        TEST_OUTPUTS_DIR,
        APP_LOGS_DIR,
        CACHE_DIR,
        DATA_DIR
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_log_file_path(component: str) -> Path:
    """
    Get the path for a component's log file.
    
    Args:
        component: Name of the component (e.g., 'main', 'browser', 'shell')
        
    Returns:
        Path to the log file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return APP_LOGS_DIR / f"{component}_{timestamp}.log"

def get_test_output_path(test_name: str) -> Path:
    """
    Get the path for test output files.
    
    Args:
        test_name: Name of the test
        
    Returns:
        Path to the test output directory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return TEST_OUTPUTS_DIR / f"{test_name}_{timestamp}"

def get_coverage_file_path() -> Path:
    """Get the path for coverage reports."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return TEST_COVERAGE_DIR / f"coverage_{timestamp}.xml"

# Create directories when module is imported
ensure_directories() 