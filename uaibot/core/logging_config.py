"""
Logging configuration for UaiBot.
Provides centralized logging setup and utilities.
"""
import logging
import os
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO):
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: The logging level to use (default: INFO)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "uaibot.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_logger(name):
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The name for the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name) 