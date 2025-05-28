"""
Configuration for output paths used throughout the application.
"""
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Define application directories
APP_LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
APP_CACHE_DIR = os.path.join(PROJECT_ROOT, 'cache')
APP_CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
APP_DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

def get_log_file_path(component: str = "app"):
    """Get the path to the log file for a specific component."""
    # Create logs directory if it doesn't exist
    os.makedirs(APP_LOGS_DIR, exist_ok=True)
    return os.path.join(APP_LOGS_DIR, f"{component}.log")

def get_cache_dir():
    """Get the path to the cache directory."""
    os.makedirs(APP_CACHE_DIR, exist_ok=True)
    return APP_CACHE_DIR

def get_config_dir():
    """Get the path to the config directory."""
    os.makedirs(APP_CONFIG_DIR, exist_ok=True)
    return APP_CONFIG_DIR

def get_data_dir():
    """Get the path to the data directory."""
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    return APP_DATA_DIR 