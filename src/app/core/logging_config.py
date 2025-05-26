"""
Logging configuration for UaiBot.
Provides centralized logging setup and utilities.
"""
import logging
import os
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_dir: str = "logs", quiet_mode: bool = False) -> None:
    """Set up the basic logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(str(log_dir / "uaibot.log")),
            logging.StreamHandler() if not quiet_mode else logging.NullHandler()
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name) 