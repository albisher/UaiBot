"""
Configuration management module for UaiBot.

This module provides centralized configuration management for the UaiBot application.
It handles loading, validating, and accessing configuration settings from various sources,
including environment variables, configuration files, and command-line arguments.

The module includes:
- Configuration loading and validation
- Environment variable handling
- Default value management
- Configuration file support
- Type conversion and validation

Example:
    >>> config = ConfigManager()
    >>> model_type = config.get("model_type", "local")
    >>> api_key = config.get("google_api_key")
"""
import os
import json
import logging
from typing import Any, Dict, Optional, Union, List, TypeVar, Generic
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')
ConfigValue = TypeVar('ConfigValue', str, int, float, bool, List, Dict)

class ConfigManager:
    """
    A class to manage configuration settings for UaiBot.
    
    This class provides a centralized way to manage configuration settings,
    supporting multiple configuration sources and validation. It handles:
    - Environment variables
    - Configuration files
    - Default values
    - Type conversion
    - Value validation
    
    Attributes:
        config_dir (str): Directory for configuration files
        config_file (str): Path to the main configuration file
        config (Dict[str, Any]): Current configuration settings
        env_prefix (str): Prefix for environment variables
    """
    
    def __init__(self, config_dir: str = "config", config_file: str = "config.json",
                 env_prefix: str = "UAIBOT_") -> None:
        """
        Initialize the ConfigManager.
        
        Args:
            config_dir (str): Directory for configuration files. Defaults to "config".
            config_file (str): Name of the main configuration file. Defaults to "config.json".
            env_prefix (str): Prefix for environment variables. Defaults to "UAIBOT_".
            
        Note:
            The configuration directory will be created if it doesn't exist.
        """
        self.config_dir: str = config_dir
        self.config_file: str = os.path.join(config_dir, config_file)
        self.env_prefix: str = env_prefix
        self.config: Dict[str, Any] = {}
        
        # Create config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Load configuration from all available sources.
        
        This method:
        1. Loads default configuration
        2. Loads configuration from file if it exists
        3. Overrides with environment variables
        4. Validates the final configuration
        
        Note:
            Environment variables take precedence over file settings,
            which take precedence over default values.
        """
        # Start with default configuration
        self.config = self._get_default_config()
        
        # Load from file if it exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            except Exception as e:
                logger.error(f"Error loading configuration file: {e}")
        
        # Override with environment variables
        self._load_from_env()
        
        # Validate configuration
        self._validate_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration settings.
        
        Returns:
            Dict[str, Any]: Dictionary containing default configuration values
        """
        return {
            "model_type": "local",
            "google_api_key": "",
            "google_model_name": "gemini-pro",
            "ollama_base_url": "http://localhost:11434",
            "quiet_mode": False,
            "log_dir": "logs",
            "log_level": "INFO",
            "max_history": 10,
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024
        }
    
    def _load_from_env(self) -> None:
        """
        Load configuration from environment variables.
        
        This method:
        1. Iterates through all configuration keys
        2. Checks for corresponding environment variables
        3. Updates configuration with environment values
        
        Note:
            Environment variables should be prefixed with self.env_prefix
            and use uppercase with underscores (e.g., UAIBOT_MODEL_TYPE).
        """
        for key in self.config:
            env_key = f"{self.env_prefix}{key.upper()}"
            if env_key in os.environ:
                value = os.environ[env_key]
                # Convert value to appropriate type
                self.config[key] = self._convert_value(value, type(self.config[key]))
    
    def _convert_value(self, value: str, target_type: type) -> Any:
        """
        Convert a string value to the target type.
        
        Args:
            value (str): String value to convert
            target_type (type): Target type for conversion
            
        Returns:
            Any: Converted value of the target type
            
        Raises:
            ValueError: If conversion fails
        """
        try:
            if target_type == bool:
                return value.lower() in ('true', '1', 'yes', 'y')
            elif target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == list:
                return json.loads(value)
            elif target_type == dict:
                return json.loads(value)
            else:
                return value
        except Exception as e:
            raise ValueError(f"Error converting value '{value}' to {target_type}: {e}")
    
    def _validate_config(self) -> None:
        """
        Validate the current configuration.
        
        This method:
        1. Checks for required values
        2. Validates value types
        3. Ensures values are within acceptable ranges
        
        Raises:
            ValueError: If validation fails
        """
        # Validate model type
        if self.config["model_type"] not in ["local", "google", "ollama"]:
            raise ValueError(f"Invalid model type: {self.config['model_type']}")
        
        # Validate Google configuration
        if self.config["model_type"] == "google" and not self.config["google_api_key"]:
            raise ValueError("Google API key is required for Google model type")
        
        # Validate numeric ranges
        if not 0 <= self.config["temperature"] <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        if not 0 <= self.config["top_p"] <= 1:
            raise ValueError("Top P must be between 0 and 1")
        if self.config["top_k"] < 1:
            raise ValueError("Top K must be greater than 0")
        if self.config["max_output_tokens"] < 1:
            raise ValueError("Max output tokens must be greater than 0")
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key (str): Configuration key
            default (Optional[Any]): Default value if key is not found
            
        Returns:
            Any: Configuration value or default value
            
        Raises:
            KeyError: If key is not found and no default is provided
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key (str): Configuration key
            value (Any): Value to set
            
        Note:
            The configuration file is not automatically saved.
            Call save() to persist changes.
        """
        self.config[key] = value
    
    def save(self) -> None:
        """
        Save the current configuration to file.
        
        This method:
        1. Validates the current configuration
        2. Creates a backup of the existing file if it exists
        3. Writes the new configuration to file
        
        Raises:
            IOError: If file operations fail
        """
        # Validate before saving
        self._validate_config()
        
        # Create backup if file exists
        if os.path.exists(self.config_file):
            backup_file = f"{self.config_file}.bak"
            try:
                os.replace(self.config_file, backup_file)
            except Exception as e:
                logger.error(f"Error creating backup: {e}")
        
        # Write new configuration
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            # Restore backup if save failed
            if os.path.exists(f"{self.config_file}.bak"):
                os.replace(f"{self.config_file}.bak", self.config_file)
            raise
    
    def reload(self) -> None:
        """
        Reload configuration from all sources.
        
        This method:
        1. Clears the current configuration
        2. Reloads from all sources
        3. Validates the new configuration
        """
        self.config.clear()
        self._load_config()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dict[str, Any]: Dictionary containing all configuration values
        """
        return self.config.copy() 