"""
Logging configuration for UaiBot.
Sets up proper logging to avoid duplicate logs and maintain consistent output.
"""
import logging
import sys
import os
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Configure logging for the application to prevent duplicate logs
    
    Args:
        log_level: The logging level (default: INFO)
        log_file: Optional log file path
    """
    # Clear any existing handlers to prevent duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure the root logger
    root_logger.setLevel(log_level)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        # Make sure the log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers to prevent propagation and duplicate messages
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.handlers = []  # Remove existing handlers
        logger.propagate = False  # Prevent propagation to root logger
        
    return root_logger
