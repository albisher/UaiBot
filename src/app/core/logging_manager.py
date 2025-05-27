"""
Logging management module for Labeeb.

This module provides centralized logging configuration and management for the Labeeb application.
It handles log file creation, log level configuration, and module-specific logger setup.
The module supports both file and console logging, with the ability to toggle console output
through quiet mode.

Example:
    >>> config = ConfigManager()
    >>> logging_manager = LoggingManager(config)
    >>> logger = logging_manager.get_logger("my_module")
    >>> logger.info("This is a test message")
"""
import logging
import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Union, TypeVar, Protocol, Set
from dataclasses import dataclass, field
from pathlib import Path
from .config_manager import ConfigManager

# Type variables
T = TypeVar('T')
HandlerType = TypeVar('HandlerType', bound=logging.Handler)

@dataclass
class LoggingConfig:
    """Configuration for logging settings."""
    log_level: str = "INFO"
    log_dir: str = "logs"
    quiet_mode: bool = False
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format: str = '%Y-%m-%d %H:%M:%S'
    modules: Set[str] = field(default_factory=lambda: {
        'core.ai_handler',
        'core.model_manager',
        'core.query_processor',
        'core.system_info_gatherer',
        'command_processor.command_processor',
        'command_processor.screen_session_manager',
        'command_processor.usb_query_handler',
        'command_processor.folder_search_handler',
        'command_processor.direct_execution_handler'
    })
    last_updated: datetime = field(default_factory=datetime.now)

class LoggingManager:
    """
    A class to manage logging configuration and operations for Labeeb.
    
    This class provides a centralized way to configure and manage logging across
    the application. It supports:
    - File-based logging with timestamped log files
    - Console logging with quiet mode toggle
    - Module-specific logger configuration
    - Dynamic log level adjustment
    
    Attributes:
        config (ConfigManager): Configuration manager instance
        log_dir (Path): Directory where log files are stored
        quiet_mode (bool): If True, suppresses console output
        logging_config (LoggingConfig): Current logging configuration
    """
    
    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize the LoggingManager.
        
        Args:
            config (ConfigManager): Configuration manager instance
            
        Note:
            The log directory will be created if it doesn't exist.
        """
        self.config = config
        self.logging_config = LoggingConfig(
            log_level=config.get("log_level", "INFO"),
            log_dir=config.get("log_dir", "logs"),
            quiet_mode=config.get("quiet_mode", False)
        )
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """
        Set up the basic logging configuration.
        
        This method:
        1. Creates the log directory if it doesn't exist
        2. Generates a timestamped log filename
        3. Configures the root logger with file and console handlers
        4. Sets up module-specific loggers
        
        The log format includes timestamp, logger name, log level, and message.
        """
        # Create logs directory if it doesn't exist
        log_dir = Path(self.logging_config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate log filename with timestamp
        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file: Path = log_dir / f"Labeeb_{timestamp}.log"
        
        # Configure root logger
        logging.basicConfig(
            level=self._get_log_level(),
            format=self.logging_config.log_format,
            datefmt=self.logging_config.date_format,
            handlers=[
                logging.FileHandler(str(log_file)),
                logging.StreamHandler() if not self.logging_config.quiet_mode else logging.NullHandler()
            ]
        )
        
        # Set up specific loggers
        self._setup_module_loggers()
    
    def _get_log_level(self) -> int:
        """
        Get the configured log level.
        
        Returns:
            int: The configured log level
            
        Note:
            The log level is read from the configuration and converted
            from string to the appropriate logging constant.
        """
        level_str = self.logging_config.log_level.upper()
        return getattr(logging, level_str, logging.INFO)
    
    def _setup_module_loggers(self) -> None:
        """
        Set up loggers for specific modules in the application.
        
        This method configures loggers for all major components of Labeeb,
        ensuring consistent logging behavior across the application.
        Each logger is set to the configured log level.
        """
        log_level = self._get_log_level()
        for module in self.logging_config.modules:
            logger = logging.getLogger(module)
            logger.setLevel(log_level)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name (str): Name of the module or component
            
        Returns:
            logging.Logger: Configured logger instance for the specified module
            
        Example:
            >>> logger = logging_manager.get_logger("my_module")
            >>> logger.info("This is a test message")
        """
        return logging.getLogger(name)
    
    def set_level(self, level: int) -> None:
        """
        Set the logging level for all loggers in the application.
        
        Args:
            level (int): Logging level to set (e.g., logging.INFO, logging.DEBUG)
            
        Note:
            This affects both the root logger and all module-specific loggers.
            Common levels include:
            - logging.DEBUG (10): Detailed information for debugging
            - logging.INFO (20): General information about program execution
            - logging.WARNING (30): Warning messages for potentially problematic situations
            - logging.ERROR (40): Error messages for serious problems
            - logging.CRITICAL (50): Critical errors that may lead to program termination
        """
        # Update configuration
        level_name = logging.getLevelName(level)
        self.logging_config.log_level = level_name
        self.logging_config.last_updated = datetime.now()
        self.config.set("log_level", level_name)
        self.config.save()
        
        # Update loggers
        logging.getLogger().setLevel(level)
        for handler in logging.getLogger().handlers:
            handler.setLevel(level)
    
    def set_quiet_mode(self, quiet: bool) -> None:
        """
        Set quiet mode, which controls whether logs are printed to console.
        
        Args:
            quiet (bool): If True, logs will not be printed to console
            
        Note:
            This method:
            1. Updates the quiet_mode setting
            2. Removes all existing handlers from the root logger
            3. Adds appropriate handlers based on the new quiet mode setting
            
            When quiet mode is enabled, logs are still written to the log file
            but are not displayed in the console.
        """
        # Update configuration
        self.logging_config.quiet_mode = quiet
        self.logging_config.last_updated = datetime.now()
        self.config.set("quiet_mode", quiet)
        self.config.save()
        
        # Update handlers
        root_logger: logging.Logger = logging.getLogger()
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add appropriate handlers based on quiet mode
        if not quiet:
            root_logger.addHandler(logging.StreamHandler())
    
    def get_current_log_file(self) -> Optional[Path]:
        """
        Get the path of the current log file.
        
        Returns:
            Optional[Path]: Path to the current log file, or None if not found
            
        Note:
            This method searches through all handlers of the root logger
            to find the first FileHandler and returns its filename.
            If no FileHandler is found, returns None.
        """
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.FileHandler):
                return Path(handler.baseFilename)
        return None 