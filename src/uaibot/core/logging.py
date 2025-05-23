"""Logging configuration for UaiBot."""

import logging
import sys
from pathlib import Path
from typing import Optional

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Name of the logger
        level: Optional logging level (defaults to INFO)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if level is None:
        level = logging.INFO
        
    logger.setLevel(level)
    
    # Create handlers if they don't exist
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # File handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(
            log_dir / f"{name}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add formatter to handlers
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger 