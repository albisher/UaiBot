"""
Logging configuration for UaiBot.
Sets up proper logging to avoid duplicate logs and maintain consistent output.
"""
import logging
import logging.handlers
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from .config.output_paths import get_log_file_path, APP_LOGS_DIR
from app.platform_core.platform_manager import PlatformManager

logger = logging.getLogger(__name__)

class StructuredLogFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

def setup_logging(
    component: str,
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Set up logging configuration with both file and console handlers.
    
    Args:
        component: Name of the component (e.g., 'main', 'browser', 'shell')
        log_level: The logging level to use
        max_bytes: Maximum size of each log file
        backup_count: Number of backup log files to keep
    """
    # Get log file path for the component
    log_file = get_log_file_path(component)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = logging.handlers.RotatingFileHandler(
        str(log_file),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_formatter = StructuredLogFormatter()
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Set logging levels for specific modules
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The name for the logger
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)

class LoggingConfig:
    def __init__(self):
        self.platform_manager = PlatformManager()
        self.platform_info = self.platform_manager.get_platform_info()
        self.handlers = self.platform_manager.get_handlers()
        self.log_path = os.path.join(self.platform_info['paths']['logs'], 'labeeb.log')

    def configure_logging(self) -> None:
        """Configure logging based on platform"""
        try:
            # Create logs directory if it doesn't exist
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

            # Configure logging format
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            date_format = '%Y-%m-%d %H:%M:%S'

            # Configure root logger
            logging.basicConfig(
                level=logging.INFO,
                format=log_format,
                datefmt=date_format,
                handlers=[
                    logging.FileHandler(self.log_path),
                    logging.StreamHandler()
                ]
            )

            # Configure platform-specific logging
            if self.platform_info['name'] == 'mac':
                self._configure_mac_logging()
            elif self.platform_info['name'] == 'windows':
                self._configure_windows_logging()
            elif self.platform_info['name'] == 'ubuntu':
                self._configure_ubuntu_logging()

            logger.info(f"Logging configured for {self.platform_info['name']}")

        except Exception as e:
            logger.error(f"Error configuring logging: {str(e)}")
            raise

    def _configure_mac_logging(self) -> None:
        """Configure macOS-specific logging"""
        try:
            # Add macOS-specific log handlers
            mac_log_path = os.path.join(self.platform_info['paths']['logs'], 'mac_specific.log')
            mac_handler = logging.FileHandler(mac_log_path)
            mac_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logging.getLogger('mac').addHandler(mac_handler)
        except Exception as e:
            logger.error(f"Error configuring macOS logging: {str(e)}")

    def _configure_windows_logging(self) -> None:
        """Configure Windows-specific logging"""
        try:
            # Add Windows-specific log handlers
            windows_log_path = os.path.join(self.platform_info['paths']['logs'], 'windows_specific.log')
            windows_handler = logging.FileHandler(windows_log_path)
            windows_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logging.getLogger('windows').addHandler(windows_handler)
        except Exception as e:
            logger.error(f"Error configuring Windows logging: {str(e)}")

    def _configure_ubuntu_logging(self) -> None:
        """Configure Ubuntu-specific logging"""
        try:
            # Add Ubuntu-specific log handlers
            ubuntu_log_path = os.path.join(self.platform_info['paths']['logs'], 'ubuntu_specific.log')
            ubuntu_handler = logging.FileHandler(ubuntu_log_path)
            ubuntu_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logging.getLogger('ubuntu').addHandler(ubuntu_handler)
        except Exception as e:
            logger.error(f"Error configuring Ubuntu logging: {str(e)}")

    def get_log_path(self) -> str:
        """Get the main log file path"""
        return self.log_path

    def get_platform_log_path(self) -> str:
        """Get the platform-specific log file path"""
        return os.path.join(
            self.platform_info['paths']['logs'],
            f"{self.platform_info['name']}_specific.log"
        )
